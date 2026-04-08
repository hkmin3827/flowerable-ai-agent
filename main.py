from dotenv import load_dotenv
from crewai import Crew, Process

from app.agents.flower_agents import (
    create_floral_analyst,
    create_bouquet_stylist,
    create_local_shop_matcher,
)
from app.tasks.flower_tasks import (
    create_flower_analysis_task,
    create_bouquet_styling_task,
    create_shop_matching_task,
)
from app.utils.parser import parse_shop_request

load_dotenv()

DIVIDER = "=" * 60

def run_phase1(user_situation: str) -> str:
    analyst = create_floral_analyst()
    stylist = create_bouquet_stylist()

    analysis_task = create_flower_analysis_task(analyst, user_situation)
    styling_task = create_bouquet_styling_task(stylist, analysis_task)

    crew = Crew(
        agents=[analyst, stylist],
        tasks=[analysis_task, styling_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)


def run_phase2(location: str, flower_names: str) -> str:
    matcher = create_local_shop_matcher()
    shop_task = create_shop_matching_task(matcher, location, flower_names)

    crew = Crew(
        agents=[matcher],
        tasks=[shop_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)


def print_banner():
    print(DIVIDER)
    print("  🌸 Flowerable AI 꽃 추천 챗봇 🌸")
    print("  CrewAI + Gemini 기반 멀티 에이전트")
    print(DIVIDER)
    print("  'quit' 또는 'exit' 입력 시 종료")
    print(DIVIDER)


def main():
    print_banner()

    print("\n[STEP 1] 어떤 상황이신가요? 꽃을 구매하고 싶으신 배경을 설명해주세요.")
    print("  예) '친구에게 사과하고 싶어요'")
    print("      '결혼 기념일 선물로 꽃다발을 준비하고 싶어요'")
    print("      '어머니 생신 선물을 찾고 있어요'\n")

    while True:
        user_situation = input("상황을 입력하세요 > ").strip()
        if user_situation.lower() in ("quit", "exit"):
            print("이용해주셔서 감사합니다. 🌷")
            return
        if user_situation:
            break
        print("상황을 입력해주세요.")

    print(f"\n{DIVIDER}")
    print("🔍 꽃 분석 및 부케 디자인 중입니다...")
    print(DIVIDER)

    phase1_result = run_phase1(user_situation)

    print(f"\n{DIVIDER}")
    print("[STEP 1 결과] 꽃 추천 및 부케 디자인")
    print(DIVIDER)
    print(phase1_result)
    print(DIVIDER)

    print("\n[STEP 2] 원하시는 꽃과 지역을 알려주시면 꽃집을 추천해드리겠습니다!")
    print("  예) '서울 중구에서 장미파는 꽃집 알고 싶어요'")
    print("      '해운대구에서 튤립이랑 작약 살 수 있는 꽃집 알려줘'")
    print("      '대구 수성구 국화'")
    print("      '부산에서 카네이션'  (광역 단위도 가능)")
    print("  (건너뛰려면 'skip' 입력)\n")

    while True:
        shop_input = input("지역과 꽃을 입력하세요 > ").strip()

        if shop_input.lower() in ("quit", "exit"):
            print("이용해주셔서 감사합니다. 🌷")
            return
        if shop_input.lower() == "skip":
            print("꽃집 추천을 건너뛰었습니다. 이용해주셔서 감사합니다. 🌷")
            break
        if not shop_input:
            print("입력값이 없습니다. 다시 입력해주세요.")
            continue

        location, flower_names = parse_shop_request(shop_input)

        if not location:
            print("⚠️  지역을 인식하지 못했습니다. 지역명을 포함해 다시 입력해주세요.")
            print("  예) '서울', '부산', '경기', '대전' 등")
            continue
        if not flower_names:
            print("⚠️  꽃 이름을 인식하지 못했습니다. 꽃 이름을 포함해 다시 입력해주세요.")
            print("  예) '장미', '튤립', '수국' 등")
            continue

        print(f"\n{DIVIDER}")
        print(f"🔍 [{location}] 지역에서 [{flower_names}] 보유 꽃집을 검색 중입니다...")
        print(DIVIDER)

        phase2_result = run_phase2(location, flower_names)

        print(f"\n{DIVIDER}")
        print("[STEP 2 결과] 꽃집 추천")
        print(DIVIDER)
        print(phase2_result)
        print(DIVIDER)

        print("\n다른 지역이나 꽃으로 다시 검색하시겠습니까? (y/n)")
        again = input("> ").strip().lower()
        if again != "y":
            break

    print("\n꽃다발로 마음을 전하세요. 감사합니다! 🌸")


if __name__ == "__main__":
    main()
