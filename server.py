"""
Flowerable AI Agent - FastAPI Server
Spring Boot ↔ CrewAI 사이의 API 서버

[실행 방법]
  uvicorn server:app --host 0.0.0.0 --port 8000 --reload

[환경변수]
  GOOGLE_API_KEY  : Gemini API 키 (필수)
  DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD : PostgreSQL 연결 정보

[동작]
  POST /recommend
    - location 없음  → Phase 1만 (꽃 추천 + 부케 디자인)
    - location 있음  → Phase 1 + Phase 2 (꽃 추천 + 꽃집 매칭)
  데이터는 요청 단위로 처리되며 서버에 저장하지 않음 (휘발성).
"""

import os
import re
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from crewai import Crew, Process

load_dotenv()

# ── Pydantic 모델 ─────────────────────────────────────────────

class RecommendRequest(BaseModel):
    purpose: str = Field(..., min_length=1, max_length=300,
                         description="사용자 상황 (예: '친구에게 사과하고 싶어요')")
    location: Optional[str] = Field(None, max_length=50,
                                    description="지역명. 없으면 꽃 추천만 수행.")


class FlowerItem(BaseModel):
    name: str
    floralLang: str
    role: str  # "메인" | "서브" | "필러"


class ShopItem(BaseModel):
    shopName: str
    address: str
    district: str
    availableFlowers: list[str]


class RecommendResponse(BaseModel):
    recommendation: str          # 마크다운 전체 추천 텍스트
    flowers: list[FlowerItem]
    shops: list[ShopItem]
    phase: str                   # "FLOWER_ONLY" | "FLOWER_AND_SHOP"


# ── FastAPI App ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
    yield

app = FastAPI(
    title="Flowerable AI Agent",
    description="CrewAI 기반 꽃 추천 + 꽃집 매칭 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── 헬퍼: CrewAI 결과에서 구조화 데이터 추출 ────────────────────

def _extract_flowers_from_text(text: str) -> list[FlowerItem]:
    """
    마크다운 텍스트에서 꽃 이름 + 꽃말 + 역할을 추출한다.
    예: "**장미**: 사랑" → FlowerItem(name='장미', floralLang='사랑', role='메인')
    """
    items: list[FlowerItem] = []

    role_sections = {
        "메인": r"### 메인 꽃(.*?)(?=###|\Z)",
        "서브": r"### 서브 꽃(.*?)(?=###|\Z)",
        "필러": r"### 필러.*?(.*?)(?=###|\Z)",
    }
    for role, pattern in role_sections.items():
        section = re.search(pattern, text, re.DOTALL)
        if not section:
            continue
        for m in re.finditer(r"\*\*(.+?)\*\*.*?[:：]\s*(.+?)(?:\s*—|\n|$)", section.group(1)):
            items.append(FlowerItem(
                name=m.group(1).strip(),
                floralLang=m.group(2).strip(),
                role=role,
            ))
    return items


def _extract_shops_from_text(text: str) -> list[ShopItem]:
    """
    마크다운 표에서 꽃집 정보를 추출한다.
    | 꽃집 이름 | 주소 | 보유 꽃 | 형식 파싱
    """
    items: list[ShopItem] = []
    rows = re.findall(r"\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", text)
    for row in rows:
        shop_name, address, flowers_raw = row
        # "장미, 튤립" → ["장미", "튤립"]
        flowers = [f.strip() for f in re.split(r"[,，、]", flowers_raw) if f.strip()]
        items.append(ShopItem(
            shopName=shop_name.strip(),
            address=address.strip(),
            district="",
            availableFlowers=flowers,
        ))
    return items


# ── 엔드포인트 ─────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """
    꽃 추천 엔드포인트.
    - location 없음 → FLOWER_ONLY (Phase 1)
    - location 있음 → FLOWER_AND_SHOP (Phase 1 + Phase 2)
    """
    # 지연 임포트: lifespan 이후 API 키 보장된 상태에서 초기화
    from app.agents.flower_agents import create_floral_analyst, create_bouquet_stylist, create_local_shop_matcher
    from app.tasks.flower_tasks import (
        create_flower_analysis_task,
        create_bouquet_styling_task,
        create_shop_matching_task,
    )

    try:
        # ── Phase 1: 꽃 추천 + 부케 디자인 ──────────────────────
        analyst = create_floral_analyst()
        stylist = create_bouquet_stylist()

        analysis_task = create_flower_analysis_task(analyst, req.purpose)
        styling_task = create_bouquet_styling_task(stylist, analysis_task)

        phase1_crew = Crew(
            agents=[analyst, stylist],
            tasks=[analysis_task, styling_task],
            process=Process.sequential,
            verbose=False,
        )
        phase1_result = str(phase1_crew.kickoff())

        flowers = _extract_flowers_from_text(phase1_result)
        shops: list[ShopItem] = []
        phase = "FLOWER_ONLY"
        full_recommendation = phase1_result

        # ── Phase 2: 꽃집 매칭 (location 있을 때만) ─────────────
        if req.location and req.location.strip():
            flower_names = ",".join(f.name for f in flowers) if flowers else ""
            if flower_names:
                matcher = create_local_shop_matcher()
                shop_task = create_shop_matching_task(
                    matcher, req.location.strip(), flower_names
                )
                phase2_crew = Crew(
                    agents=[matcher],
                    tasks=[shop_task],
                    process=Process.sequential,
                    verbose=False,
                )
                phase2_result = str(phase2_crew.kickoff())
                shops = _extract_shops_from_text(phase2_result)
                full_recommendation = f"{phase1_result}\n\n---\n\n{phase2_result}"
                phase = "FLOWER_AND_SHOP"

        return RecommendResponse(
            recommendation=full_recommendation,
            flowers=flowers,
            shops=shops,
            phase=phase,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 에이전트 처리 중 오류: {str(e)}")
