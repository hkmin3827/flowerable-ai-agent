import os
import re
import json
from contextlib import asynccontextmanager
from typing import Literal
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crewai import Crew, Process

from app.dto.schemas import ContentReq, FlowerItem, ShopItem, RecommendRes
from app.tools.flower_tools import (
    _resolve_location_internal,
    _search_by_district,
    _search_by_region,
)
from app.utils.constant import _ALL_FLOWERS, _ALL_FLOWERS_SET, _SHOP_INTENT_KEYWORDS, _LOCATION_NOT_FOUND_MSG

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    yield


app = FastAPI(
    title="Flowerable AI Agent",
    description="CrewAI 기반 꽃 추천 + 꽃집 매칭 API (단일 엔드포인트, 자동 Phase 판단)",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def _detect_phase(content: str) -> Literal["exit", "1", "2"]:
    if content.strip().lower() in ("exit", "quit"):
        return "exit"

    loc = _resolve_location_internal(content)
    if loc["status"] == "NOT_FOUND":
        return "1"

    has_shop_intent = any(kw in content for kw in _SHOP_INTENT_KEYWORDS)
    has_flower_name = any(f in content for f in _ALL_FLOWERS_SET)
    return "2" if (has_shop_intent or has_flower_name) else "1"


def _extract_flowers_from_content(content: str) -> list[str]:
    return [f for f in _ALL_FLOWERS if f in content]


def _extract_flowers_from_text(text: str) -> list[FlowerItem]:
    items: list[FlowerItem] = []
    role_sections = {
        "메인": r"### 메인 꽃(.*?)(?=###|\Z)",   # Stylist 출력: "### 메인 꽃 (베스트 선정)"
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


def _build_shops(raw: dict) -> tuple[list[ShopItem], str | None]:
    """
    _search_by_district / _search_by_region 결과 dict에서
    ShopItem 리스트와 fallback 메시지를 추출한다.
    shopId는 DB row에서 직접 가져오므로 유실 없음.
    """
    shops_data: list[dict] = raw.get("shops") or []
    fallback_raw: list = raw.get("nearby_alternatives") or []
    fallback_msg: str | None = raw.get("message")

    if not shops_data and fallback_raw:
        for item in fallback_raw:
            if isinstance(item, dict) and "shops" in item:
                # region-level fallback: {"region": .., "shops": [...]}
                shops_data.extend(item["shops"])
            elif isinstance(item, dict) and "shopId" in item:
                # district-level fallback: shop dict 직접
                shops_data.append(item)

    shops = [
        ShopItem(
            shopId=s.get("shopId", 0),
            shopName=s.get("shopName", ""),
            address=s.get("address", ""),
            district=s.get("district", ""),
            availableFlowers=s.get("availableFlowers") or [],
        )
        for s in shops_data
    ]
    message = fallback_msg if not shops_data else None
    return shops, message


def _parse_location_json(agent_output: str) -> dict | None:
    """LocationParser agent 텍스트 출력에서 JSON 블록을 추출·파싱한다."""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", agent_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    match = re.search(r"\{[^{}]*\"status\"[^{}]*\}", agent_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendRes)
async def recommend(req: ContentReq):
    print(f"\n🚀 [Spring 요청 수신 성공] 내용: {req.content}")

    phase = _detect_phase(req.content)

    if phase == "exit":
        return RecommendRes(phase="END")

    if phase == "1":
        return await _run_phase1(req.content)

    return await _run_phase2(req.content)


async def _run_phase1(content: str) -> RecommendRes:
    from app.agents.flower_agents import create_floral_analyst, create_bouquet_stylist
    from app.tasks.flower_tasks import create_flower_analysis_task, create_bouquet_styling_task

    try:
        analyst = create_floral_analyst()
        stylist = create_bouquet_stylist()

        analysis_task = create_flower_analysis_task(analyst, content)
        styling_task = create_bouquet_styling_task(stylist, analysis_task)

        crew = Crew(
            agents=[analyst, stylist],
            tasks=[analysis_task, styling_task],
            process=Process.sequential,
            verbose=True,
        )
        result = await asyncio.wait_for(
            asyncio.to_thread(crew.kickoff),
            timeout=18.0
        )
        flowers = _extract_flowers_from_text(result)

        return RecommendRes(
            phase="FLOWER_ONLY",
            recommendation=result,
            flowers=flowers,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"꽃 추천 처리 중 오류: {str(e)}")


async def _run_phase2(content: str) -> RecommendRes:
    """
    Phase 2 흐름:
      1. _detect_phase 에서 이미 위치 코드 존재를 확인했으므로
         _resolve_location_internal 을 재사용해 location 코드를 얻는다. (LLM 없음)
      2. ALL_FLOWERS 키워드 매칭으로 꽃 이름 추출. (LLM 없음)
      3. DB 내부 함수 직접 호출 → shopId 포함 완전한 ShopItem 반환.

      단, 위치 애매(중구 등 중복)로 인해 _resolve_location_internal이 지역을 못 잡을 경우
      LocationParser 에이전트(LLM) 를 fallback으로 사용한다.
    """
    try:
        loc = _resolve_location_internal(content)
        region_code = loc.get("region_code", "")
        district_code = loc.get("district_code", "")
        address_hint = loc.get("address_hint", "")

        if loc["status"] == "NOT_FOUND" or (not region_code and not district_code):
            from app.agents.flower_agents import create_location_parser
            from app.tasks.flower_tasks import create_location_parsing_task

            parser = create_location_parser()
            parse_task = create_location_parsing_task(parser, content)
            parse_crew = Crew(
                agents=[parser], tasks=[parse_task],
                process=Process.sequential, verbose=True,
            )
            parse_output = await asyncio.wait_for(
            asyncio.to_thread(parse_crew.kickoff),
            timeout=18.0
            )
            location_data = _parse_location_json(parse_output)

            if not location_data or location_data.get("status") == "NOT_FOUND":
                return RecommendRes(
                    phase="LOCATION_NOT_FOUND",
                    message=_LOCATION_NOT_FOUND_MSG,
                )
            region_code = location_data.get("region_code", "")
            district_code = location_data.get("district_code", "")
            address_hint = location_data.get("address_hint", "")

        if not region_code and not district_code:
            return RecommendRes(
                phase="LOCATION_NOT_FOUND",
                message=_LOCATION_NOT_FOUND_MSG,
            )

        flower_names = _extract_flowers_from_content(content)

        # ──  DB 직접 조회 (shopId 보존) ────────────────────────────────
        location_code = district_code if district_code else region_code
        if district_code:
            raw = json.loads(_search_by_district(district_code, flower_names, address_hint))
        else:
            raw = json.loads(_search_by_region(region_code, flower_names, address_hint))

        shops, message = _build_shops(raw)
        phase = "FLOWER_AND_SHOP" if shops else "LOCATION_NOT_FOUND"

        return RecommendRes(
            phase=phase,
            shops=shops if shops else [],
            message=message,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"꽃집 추천 처리 중 오류: {str(e)}")
