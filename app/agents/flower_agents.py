from crewai import Agent
from app.tools.flower_tools import (
    get_flowers_by_sentiment,
    get_matching_sub_flowers,
    get_shops_by_location_and_flower,
)
from app.core.model import model


def create_floral_analyst() -> Agent:
    """
    Floral Analyst: 사용자 상황을 분석하여 DB에 존재하는 꽃 중 가장 적합한 메인 꽃을 선정.
    - 환각 방지: 반드시 get_flowers_by_sentiment 도구 결과만 사용
    """
    return Agent(
        role="Floral Analyst",
        goal=(
            "사용자의 상황과 감정을 분석하여, DB에 등록된 꽃들 중에서 "
            "의미(꽃말)가 가장 적절한 '메인 꽃' 1~3가지를 선정한다. "
            "절대로 도구가 반환하지 않은 꽃을 추천해서는 안 된다."
            "의미가 연관이 아예 없다고 판단되면 개수를 채우기 위해 억지로 메인 꽃에 끼워맞추지 않는다."
        ),
        backstory=(
            "당신은 10년 경력의 플로리스트이자 꽃말 전문가입니다. "
            "사람들의 이야기를 듣고 그 감정에 꼭 맞는 꽃의 언어를 찾아내는 것이 특기입니다. "
            "당신은 항상 실제 DB에 존재하는 꽃만 추천하며, "
            "존재하지 않는 꽃을 만들어내는 일은 절대 하지 않습니다."
        ),
        tools=[get_flowers_by_sentiment],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_bouquet_stylist() -> Agent:
    """
    Bouquet Stylist: 메인 꽃과 어울리는 서브 꽃·필러 소재를 DB에서 조합하여 부케 디자인 제안.
    """
    return Agent(
        role="Bouquet Stylist",
        goal=(
            "Floral Analyst가 선정한 메인 꽃 중 가장 사용자의 상황과 꽃말이 알맞는 꽃을 1가지 선정하고, "
            "get_matching_sub_flowers 도구를 사용해 선정된 꽃을 제외한 가장 잘 어울리는 서브 꽃을 DB에서 등록된 꽃 중 2~3가지 선정한다."
            "그리고 필러/그린 소재를 조합하여 최종 부케 디자인을 마크다운 형식으로 제안한다. "
            "도구가 반환한 꽃 목록 외에는 절대 사용하지 않는다."
        ),
        backstory=(
            "당신은 국내외 플로럴 디자인 대회 수상 경력을 가진 부케 스타일리스트입니다. "
            "색감, 질감, 꽃말의 조화를 고려해 아름다운 부케를 구성합니다. "
            "항상 DB에 실제 등록된 꽃만 활용하며, "
            "각 꽃의 역할(메인/서브/필러)을 명확히 구분해 설명합니다."
        ),
        tools=[get_matching_sub_flowers],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_local_shop_matcher() -> Agent:
    """
    Local Shop Matcher: 사용자 지역 + 원하는 꽃을 기반으로 꽃집 3곳 추천.
    꽃집이 없을 경우 인접 지역 대안 제시.
    """
    return Agent(
        role="Local Shop Matcher",
        goal=(
            "사용자가 요청한 지역과 꽃 이름을 get_shops_by_location_and_flower 도구에 전달하여 "
            "해당 꽃을 보유한 ACTIVE 꽃집 3곳을 조회하고 마크다운 표 형식으로 안내한다. "
            "꽃집이 없으면 인접 지역의 대안 꽃집을 친절하게 제안한다."
        ),
        backstory=(
            "당신은 전국 꽃집 네트워크 데이터베이스 전문가입니다. "
            "사용자가 원하는 꽃을 가장 가까운 곳에서 구할 수 있도록 안내하는 것이 목표입니다. "
            "DB에 등록된 꽃집 정보만 제공하며, 재고가 없는 경우 솔직하게 안내하고 "
            "인근 지역의 대안을 제시합니다."
        ),
        tools=[get_shops_by_location_and_flower],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
