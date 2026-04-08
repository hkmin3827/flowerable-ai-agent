from app.utils.constant import REGIONS, ALL_FLOWERS

def parse_shop_request(user_input: str):
    """
    사용자 입력에서 지역과 꽃 이름을 추출합니다.
    예: "서울에서 장미 사고 싶어" → ("서울", "장미")
        "부산 튤립 작약" → ("부산", "튤립,작약")
    """
    detected_region = None
    detected_flowers = []

    for r in sorted(REGIONS, key=len, reverse=True):
        if r in user_input:
            detected_region = r
            break

    for f in ALL_FLOWERS:
        if f in user_input:
            detected_flowers.append(f)

    return detected_region, ",".join(detected_flowers) if detected_flowers else None
