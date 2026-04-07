"""
Flowerable CrewAI - Task 정의
Phase 1: 꽃 분석 + 부케 스타일링
Phase 2: 지역 꽃집 매칭
"""
from crewai import Task
from crewai import Agent


def create_flower_analysis_task(agent: Agent, user_situation: str) -> Task:
    """
    Task 1 - Floral Analyst: 상황 분석 → 메인 꽃 선정
    """
    return Task(
        description=f"""
사용자의 상황을 분석하여 DB에서 가장 적합한 메인 꽃을 선정하세요.

[사용자 상황]
{user_situation}

[수행 절차]
1. 사용자 상황에서 핵심 감정/키워드를 추출합니다.
   (예: '사과' → '진심,성실', '축하' → '영광,화려함,기쁨', '사랑' → '사랑,고백')
2. get_flowers_by_sentiment 도구를 호출하여 해당 감정에 맞는 꽃 목록을 조회합니다.
3. 도구가 반환한 목록에서만 메인 꽃 1~2가지를 선정합니다.

[출력 형식]
## 🌸 메인 꽃 추천

| 꽃 이름 | 꽃말 | 선정 이유 |
|--------|------|---------|
| (꽃 이름) | (꽃말) | (왜 이 상황에 적합한지 2~3줄 설명) |

> ⚠️ 도구가 반환하지 않은 꽃은 절대 포함하지 마세요.
""",
        expected_output=(
            "메인 꽃 이름(들), 꽃말, 선정 이유가 포함된 마크다운 표. "
            "반드시 DB 조회 결과에서만 선정할 것."
        ),
        agent=agent,
    )


def create_bouquet_styling_task(agent: Agent, flower_analysis_task: Task) -> Task:
    """
    Task 2 - Bouquet Stylist: 메인 꽃 기반 서브 꽃·필러 조합 설계
    """
    return Task(
        description="""
Floral Analyst가 선정한 메인 꽃을 바탕으로 조화로운 부케 디자인을 완성하세요.

[수행 절차]
1. 이전 작업(Floral Analyst)의 출력에서 메인 꽃 이름을 확인합니다.
2. get_matching_sub_flowers 도구를 메인 꽃 이름으로 호출하여 서브 꽃 후보를 조회합니다.
3. 도구 반환 목록에서만 서브 꽃 1~2가지와 필러/그린 소재 1~2가지를 선택합니다.
4. 색감, 꽃말의 조화, 계절감을 고려하여 선택 이유를 설명합니다.

[출력 형식]
## 💐 추천 부케 디자인

### 메인 꽃
- **꽃 이름**: (꽃말)

### 서브 꽃
- **꽃 이름**: (꽃말) — (선택 이유)

### 필러 / 그린 소재
- **꽃 이름**: (꽃말 또는 역할) — (선택 이유)

### 전체 디자인 컨셉
> (3~4줄로 부케의 색감, 분위기, 어울리는 상황 설명)

---
원하시는 꽃과 지역을 말씀해주시면 해당 꽃을 보유한 꽃집을 추천해드리겠습니다. 🌿
""",
        expected_output=(
            "부케 디자인 전체 구성 (메인/서브/필러 꽃 목록, 각 선택 이유, 전체 컨셉). "
            "마지막에 지역·꽃 입력 안내 문구 포함."
        ),
        agent=agent,
        context=[flower_analysis_task],
    )


def create_shop_matching_task(agent: Agent, location: str, flower_names: str) -> Task:
    """
    Task 3 - Local Shop Matcher: 지역 + 꽃 기반 꽃집 3곳 추천
    꽃집이 없으면 인접 지역 대안 제시
    """
    return Task(
        description=f"""
사용자가 요청한 지역에서 해당 꽃을 보유한 꽃집을 DB에서 조회하여 안내하세요.

[요청 정보]
- 지역: {location}
- 원하는 꽃: {flower_names}

[수행 절차]
1. get_shops_by_location_and_flower 도구를 호출합니다.
   입력 형식: "{location}|{flower_names}"
2. 결과에 따라 다음 중 하나를 수행합니다.

   [꽃집이 있는 경우]
   - 최대 3곳의 꽃집 정보를 마크다운 표로 정리합니다.
   - 각 꽃집이 보유한 꽃 목록도 함께 표시합니다.

   [꽃집이 없는 경우]
   - "{location}에는 해당 꽃을 보유한 꽃집을 찾을 수 없습니다." 라고 안내합니다.
   - 도구가 반환한 nearby_alternatives 정보를 활용하여 인근 지역 꽃집을 제안합니다.
   - "근처 지역의 다른 꽃집을 추천해드릴까요?" 라고 물어봅니다.

[출력 형식 - 꽃집 있는 경우]
## 📍 추천 꽃집 목록 ({location})

| # | 꽃집 이름 | 주소 | 보유 꽃 |
|---|---------|------|--------|
| 1 | (이름) | (주소) | (꽃 목록) |
| 2 | (이름) | (주소) | (꽃 목록) |
| 3 | (이름) | (주소) | (꽃 목록) |

[출력 형식 - 꽃집 없는 경우]
## ⚠️ 꽃집을 찾을 수 없습니다

'{location}'에는 **{flower_names}**을(를) 보유한 꽃집이 등록되어 있지 않습니다.

### 근처 지역 대안
(도구가 반환한 인근 지역 꽃집 정보 표시)

근처 지역의 다른 꽃집을 추천해드릴까요?
""",
        expected_output=(
            "꽃집 3곳 마크다운 표 (이름, 주소, 보유 꽃) 또는 "
            "꽃집 없음 안내 + 인접 지역 대안 + 추가 추천 여부 질문."
        ),
        agent=agent,
    )
