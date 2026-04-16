import json
import random
import re
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool
from contextlib import contextmanager
from crewai.tools import tool
from app.utils.constant import _NEARBY_DISTRICTS, _NEARBY_REGIONS, _REGION_CODES, _REGION_MAP, _DISTRICT_LOOKUP, _REGION_CODE_TO_KR, _DISTRICT_CODE_TO_KR
from app.core.config import DB_CONFIG
from app.core.cache import get_cached_shops, set_cached_shops
from app.utils.sql import _SQL_BY_DISTRICT_WITH_ADDR, _SQL_BY_DISTRICTS, _SQL_BY_REGIONS, _SQL_BY_REGION

_pool = None


def _get_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pg_pool.ThreadedConnectionPool(minconn=1, maxconn=5, **DB_CONFIG)
    return _pool

@contextmanager
def _get_conn():
    p = _get_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)



def _rows_to_shops(rows) -> list:
    return [
        {
            "shopId":           r["shop_id"],
            "shopName":         r["shop_name"],
            "address":          r["address"],
            "district":         r["district"],
            "availableFlowers": r["flower_names"],
        }
        for r in rows
    ]


def _is_district_code(code: str) -> bool:
    """'REGION_XXX' 형태인지 확인 (Region 코드는 언더스코어 없음)."""
    parts = code.split("_", 1)
    return len(parts) == 2 and parts[0] in _REGION_CODES

_KO_POSTPOSITIONS = (
    "에서의", "에서", "으로부터", "으로", "로부터", "로", "에게서", "에게",
    "에서도", "에도", "에만", "에는", "에", "의", "이나", "이라도",
    "이라", "이랑", "이", "가", "을", "를", "은", "는", "도", "만",
    "와", "과", "랑", "한테", "께",
)


def _strip_postposition(token: str) -> str:
    """토큰에서 한국어 조사를 제거해 원형을 반환한다. (에서, 에, 으로 등)"""
    for p in _KO_POSTPOSITIONS:
        if token.endswith(p) and len(token) > len(p):
            return token[: -len(p)]
    return token


def _resolve_location_internal(text: str) -> dict:
    """
    지역 텍스트를 DB 코드로 변환하는 내부 함수.
    '해운대구에서', '부산에서' 처럼 조사가 붙은 형태도 처리한다.
    반환: {status, region_code, district_code, address_hint}
    """
    text = text.strip()
    raw_tokens = [t for t in re.split(r"[\s,]+", text) if t]

    # 각 토큰을 조사 제거한 버전과 함께 검사
    tokens: list[str] = []
    raw_token_map: dict[str, str] = {}  # stripped 토큰 → 원본 토큰
    for t in raw_tokens:
        stripped = _strip_postposition(t)
        tokens.append(stripped)
        raw_token_map[stripped] = t

    stop_words = {"파는", "사는", "구매할", "수", "꽃집", "꽃", "근처", "주변",
                  "알려", "줘", "주세요", "있는", "어디", "찾아"}

    found_region = None
    found_district_code = None
    matched_tokens: set = set()

    # 전체 텍스트 직접 조회
    if text in _DISTRICT_LOOKUP:
        codes = _DISTRICT_LOOKUP[text]
        if len(codes) == 1:
            dc = codes[0]
            rc = dc.split("_", 1)[0]
            return {"status": "OK", "region_code": rc, "district_code": dc, "address_hint": ""}
    if text in _REGION_MAP:
        return {"status": "OK", "region_code": _REGION_MAP[text], "district_code": "", "address_hint": ""}

    # 토큰별 1차 조회
    # 원본 토큰 우선 확인: '전라남도' → strip 시 '전라남'으로 잘리는 문제 방지
    for token in tokens:
        raw = raw_token_map.get(token, token)
        region_key = raw if raw in _REGION_MAP else token
        if region_key in _REGION_MAP and not found_region:
            found_region = _REGION_MAP[region_key]
            matched_tokens.add(token)
        if token in _DISTRICT_LOOKUP and not found_district_code:
            codes = _DISTRICT_LOOKUP[token]
            if len(codes) == 1:
                found_district_code = codes[0]
                matched_tokens.add(token)

    # 중복 지역 disambiguation (중구, 동구 등 → region 컨텍스트로 구분)
    if not found_district_code:
        for token in tokens:
            if token in _DISTRICT_LOOKUP and token not in matched_tokens:
                codes = _DISTRICT_LOOKUP[token]
                if len(codes) > 1 and found_region:
                    matching = [c for c in codes if c.startswith(found_region + "_")]
                    if matching:
                        found_district_code = matching[0]
                        matched_tokens.add(token)
                        break

    # district → region 추론
    if found_district_code and not found_region:
        found_region = found_district_code.split("_", 1)[0]

    if found_region or found_district_code:
        # address_hint: 매칭 안 된 토큰 중 지역 관련 단어 (동/구 수준 세부주소)
        unmatched = [
            t for t in tokens
            if t not in matched_tokens
               and t not in _REGION_MAP
               and t not in _DISTRICT_LOOKUP
               and t not in stop_words
               and len(t) >= 2
        ]
        return {
            "status": "OK",
            "region_code": found_region or "",
            "district_code": found_district_code or "",
            "address_hint": " ".join(unmatched),
        }

    return {"status": "NOT_FOUND", "input": text}


# district → region 추론은 district_code에서 분리


# ── CrewAI 툴 ────────────────────────────────────────────────────

@tool
def resolve_location(location_text: str) -> str:
    """
    사용자 입력에서 추출한 지역 텍스트를 DB 지역 코드로 변환합니다.

    입력: 지역 관련 텍스트 (예: "해운대구", "부산 중구", "경기도 성남시 분당구")
    출력: JSON {
      "status": "OK" | "NOT_FOUND",
      "region_code": "BUSAN",           -- 광역 코드
      "district_code": "BUSAN_HAEUNDAEGU",  -- 구/시 코드 (없을 수 있음)
      "address_hint": "우동"            -- DB에 없는 세부 주소 힌트 (빈 문자열 가능)
    }
    """
    result = _resolve_location_internal(location_text)
    return json.dumps(result, ensure_ascii=False)


@tool
def get_flowers_by_sentiment(sentiment_keywords: str) -> str:
    """
    감정 키워드로 DB 꽃 목록을 조회합니다.
    입력: 쉼표로 구분된 감정 키워드 (예: "사랑,고백,행복")
    """
    keywords = [k.strip() for k in sentiment_keywords.split(",") if k.strip()]
    if not keywords:
        return json.dumps({"flowers": [], "message": "키워드를 입력해주세요."}, ensure_ascii=False)

    conditions = " OR ".join(["floral_lang ILIKE %s" for _ in keywords])
    params = [f"%{k}%" for k in keywords]
    sql = f"""
        SELECT id, name, floral_lang, category
        FROM flowers
        WHERE active = true
          AND ({conditions})
        ORDER BY id
        LIMIT 20
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        flowers = [{"id": r["id"], "name": r["name"],
                    "floralLang": r["floral_lang"], "category": r["category"]} for r in rows]
        return json.dumps({"flowers": flowers, "total": len(flowers)}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "flowers": []}, ensure_ascii=False)


@tool
def get_matching_sub_flowers(best_flower_name: str) -> str:
    """
    베스트 꽃에 어울리는 서브 꽃 후보를 DB에서 조회합니다.
    입력: 베스트 꽃 이름 (예: "장미")
    """
    filler_names = ["안개꽃", "팜파스", "목화", "수국", "소국", "스위트피", "리시안셔스"]
    sql_best = "SELECT id FROM flowers WHERE name = %s AND active = true"
    sql_others = """
        SELECT id, name, floral_lang, category,
               CASE WHEN name = ANY(%s) THEN '필러/그린' ELSE '서브꽃' END AS role
        FROM flowers
        WHERE active = true
          AND name != %s
        ORDER BY
          CASE WHEN name = ANY(%s) THEN 0 ELSE 1 END,
          id
        LIMIT 30
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql_best, (best_flower_name,))
                if not cur.fetchone():
                    return json.dumps(
                        {"error": f"'{best_flower_name}' 꽃이 DB에 존재하지 않습니다.", "flowers": []},
                        ensure_ascii=False
                    )
                cur.execute(sql_others, (filler_names, best_flower_name, filler_names))
                rows = cur.fetchall()
        flowers = [
            {"id": r["id"], "name": r["name"],
             "floralLang": r["floral_lang"], "category": r["category"], "role": r["role"]}
            for r in rows
        ]
        return json.dumps(
            {"best_flower": best_flower_name, "candidates": flowers, "total": len(flowers)},
            ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps({"error": str(e), "flowers": []}, ensure_ascii=False)


@tool
def get_shops_by_location_and_flower(location_and_flowers: str) -> str:
    """
    지역 코드와 꽃 이름으로 꽃집을 DB에서 조회합니다.

    입력 형식: "지역코드|꽃이름1,꽃이름2" 또는 "지역코드|꽃이름1,꽃이름2|세부주소힌트"
    예시:
      "BUSAN_HAEUNDAEGU|장미,튤립"
      "GYEONGGI_SEONGNAM|장미|분당구"   ← 세부 주소 필터 포함
      "BUSAN|장미"                       ← region 레벨 (district 없을 때)

    출력: JSON { shops: [...], count, location, location_type }
    """
    try:
        parts = location_and_flowers.split("|")
        if len(parts) < 2:
            return json.dumps(
                {"error": "입력 형식 오류. '지역코드|꽃이름1,꽃이름2' 형식으로 입력하세요."},
                ensure_ascii=False
            )
        location_raw = parts[0].strip()
        flower_names = [f.strip() for f in parts[1].split(",") if f.strip()]
        address_hint = parts[2].strip() if len(parts) >= 3 else ""

        if _is_district_code(location_raw):
            return _search_by_district(location_raw, flower_names, address_hint)
        elif location_raw in _REGION_CODES:
            return _search_by_region(location_raw, flower_names, address_hint)
        else:
            return json.dumps(
                {"error": f"'{location_raw}'은(는) 알 수 없는 지역 코드입니다.", "shops": []},
                ensure_ascii=False
            )
    except Exception as e:
        return json.dumps({"error": str(e), "shops": []}, ensure_ascii=False)


def _sample(shops: list[dict], n: int = 3) -> list[dict]:
    return random.sample(shops, min(n, len(shops)))


def _search_by_district(district_code: str, flower_names: list, address_hint: str = "") -> str:
    """District 코드로 꽃집 검색.
    캐시는 region 단위로 관리하고, district/address_hint는 Python에서 필터링.
    """
    region_code = district_code.split("_", 1)[0]
    district_kr = _DISTRICT_CODE_TO_KR.get(district_code, district_code)

    # region 캐시 or DB 조회로 region 전체 풀 확보
    all_region_shops = get_cached_shops(region_code, flower_names)
    if all_region_shops is None:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(_SQL_BY_REGION, (region_code, flower_names))
                rows = cur.fetchall()
        all_region_shops = _rows_to_shops(rows)
        if all_region_shops:
            set_cached_shops(region_code, flower_names, all_region_shops)

    # district 필터링
    pool = [s for s in all_region_shops if s.get("district") == district_code]

    # address_hint 추가 필터 (캐시 저장 안 함 — 세부 주소는 재사용성 낮음)
    if not pool and address_hint:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(_SQL_BY_DISTRICT_WITH_ADDR,
                            (district_code, flower_names, f"%{address_hint}%"))
                rows = cur.fetchall()
        if rows:
            shops = _sample(_rows_to_shops(rows))
            return json.dumps(
                {"location": district_code, "location_type": "district",
                 "shops": shops, "count": len(shops),
                 "address_hint_applied": address_hint},
                ensure_ascii=False, indent=2
            )
    elif pool and address_hint:
        filtered = [s for s in pool if address_hint in s.get("address", "")]
        if filtered:
            pool = filtered

    if pool:
        sampled = _sample(pool)
        return json.dumps(
            {"location": district_code, "location_type": "district",
             "shops": sampled, "count": len(sampled)},
            ensure_ascii=False, indent=2
        )

    # fallback: 인접 구
    nearby_districts = _NEARBY_DISTRICTS.get(district_code, [])
    if nearby_districts:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(_SQL_BY_DISTRICTS, (nearby_districts, flower_names))
                nearby_rows = cur.fetchall()
        if nearby_rows:
            return json.dumps(
                {
                    "location": district_code, "location_type": "district",
                    "shops": [], "count": 0,
                    "message": f"'{district_kr}'에는 해당 꽃을 보유한 꽃집이 없습니다.",
                    "nearby_alternatives": _sample(_rows_to_shops(nearby_rows)),
                },
                ensure_ascii=False, indent=2
            )

    # fallback: region 전체 (이미 확보한 풀 재사용)
    return json.dumps(
        {
            "location": district_code, "location_type": "district",
            "shops": [], "count": 0,
            "message": f"'{district_kr}' 및 인근 구에 해당 꽃을 보유한 꽃집이 없습니다.",
            "nearby_alternatives": _sample(all_region_shops),
        },
        ensure_ascii=False, indent=2
    )


def _search_by_region(region_code: str, flower_names: list, address_hint: str = "") -> str:
    """Region 코드로 꽃집 검색 → 인접 region fallback."""

    # 캐시 확인
    cached = get_cached_shops(region_code, flower_names)
    if cached:
        pool = cached
        if address_hint:
            filtered = [s for s in pool if address_hint in s.get("address", "")]
            if filtered:
                pool = filtered
        shops = _sample(pool)
        return json.dumps(
            {"location": region_code, "location_type": "region",
             "shops": shops, "count": len(shops), "cached": True},
            ensure_ascii=False, indent=2
        )

    # DB 조회 후 캐싱
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(_SQL_BY_REGION, (region_code, flower_names))
            rows = cur.fetchall()

    if rows:
        all_shops = _rows_to_shops(rows)
        set_cached_shops(region_code, flower_names, all_shops)

        pool = all_shops
        if address_hint:
            filtered = [s for s in pool if address_hint in s.get("address", "")]
            if filtered:
                pool = filtered

        shops = _sample(pool)
        return json.dumps(
            {"location": region_code, "location_type": "region",
             "shops": shops, "count": len(shops)},
            ensure_ascii=False, indent=2
        )

    # fallback: 인접 region
    nearby_codes = _NEARBY_REGIONS.get(region_code, [])
    nearby_results = []
    if nearby_codes:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(_SQL_BY_REGIONS, (nearby_codes, flower_names))
                nearby_rows = cur.fetchall()

        seen_regions: dict = {}
        for r in nearby_rows:
            rc = r["region"]
            if rc not in seen_regions:
                seen_regions[rc] = []
            if len(seen_regions[rc]) < 3:
                seen_regions[rc].append({
                    "shopId":           r["shop_id"],
                    "shopName":         r["shop_name"],
                    "address":          r["address"],
                    "district":         r["district"],
                    "availableFlowers": r["flower_names"],
                })
            if len(seen_regions) >= 2 and all(len(v) >= 1 for v in seen_regions.values()):
                break

        nearby_results = [
            {"region": rc, "shops": shops}
            for rc, shops in seen_regions.items()
        ]

    region_kr = _REGION_CODE_TO_KR.get(region_code, region_code)
    return json.dumps(
        {
            "location": region_code, "location_type": "region",
            "shops": [], "count": 0,
            "message": f"'{region_kr}'에는 해당 꽃을 보유한 꽃집이 없습니다.",
            "nearby_alternatives": nearby_results,
        },
        ensure_ascii=False, indent=2
    )
