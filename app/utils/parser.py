from app.utils.constant import _REGION_MAP, _DISTRICT_LOOKUP, _ALL_FLOWERS

def parse_shop_request(user_input: str):

    detected_region_code = None
    for kr in sorted(_REGION_MAP.keys(), key=len, reverse=True):
        if kr in user_input:
            detected_region_code = _REGION_MAP[kr]
            break

    detected_district_code = None
    for desc in sorted(_DISTRICT_LOOKUP.keys(), key=len, reverse=True):
        if desc not in user_input:
            continue
        candidates = _DISTRICT_LOOKUP[desc]
        if len(candidates) == 1:
            detected_district_code = candidates[0]
            break
        if detected_region_code:
            # 동명 구/시 → region 컨텍스트로 disambiguate
            filtered = [c for c in candidates if c.startswith(detected_region_code + "_")]
            if filtered:
                detected_district_code = filtered[0]
                break
        # region 없고 중복이면 스킵

    detected_flowers = [f for f in _ALL_FLOWERS if f in user_input]

    # ── 우선순위: district_code > region_code > None ──────────────────
    location = detected_district_code or detected_region_code
    return location, ",".join(detected_flowers) if detected_flowers else None
