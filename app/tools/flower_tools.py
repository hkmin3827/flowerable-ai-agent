import json
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool
from contextlib import contextmanager
from crewai.tools import tool
from app.utils.constant import NEARBY_DISTRICTS, NEARBY_REGIONS, REGION_CODES
from app.core.config import DB_CONFIG

_pool = None


def _get_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pg_pool.ThreadedConnectionPool(minconn=1, maxconn=5, **DB_CONFIG)
    return _pool


@contextmanager
def _get_conn():
    """커넥션 풀에서 커넥션을 빌려 yield하고, 완료 후 반납합니다."""
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


_SQL_BY_DISTRICT = """
    SELECT
        s.id        AS shop_id,
        s.shop_name,
        s.address,
        s.district,
        array_agg(DISTINCT f.name)                     AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1)    AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers     f  ON f.id = sf.flower_id
    WHERE s.district = %s
      AND s.status = 'ACTIVE'
      AND sf.on_sale = true
      AND f.name = ANY(%s)
      AND f.active = true
      AND s.deleted_at IS NULL
    GROUP BY s.id, s.shop_name, s.address, s.district
    HAVING array_length(array_agg(DISTINCT f.name), 1) > 0
    ORDER BY match_count DESC, s.id
    LIMIT 3
"""

_SQL_BY_DISTRICTS = """
    SELECT
        s.id        AS shop_id,
        s.shop_name,
        s.address,
        s.district,
        array_agg(DISTINCT f.name)                     AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1)    AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers     f  ON f.id = sf.flower_id
    WHERE s.district = ANY(%s)
      AND s.status = 'ACTIVE'
      AND sf.on_sale = true
      AND f.name = ANY(%s)
      AND f.active = true
      AND s.deleted_at IS NULL
    GROUP BY s.id, s.shop_name, s.address, s.district
    HAVING array_length(array_agg(DISTINCT f.name), 1) > 0
    ORDER BY match_count DESC, s.id
    LIMIT 6
"""

_SQL_BY_REGION = """
    SELECT
        s.id        AS shop_id,
        s.shop_name,
        s.address,
        s.district,
        array_agg(DISTINCT f.name)                     AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1)    AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers     f  ON f.id = sf.flower_id
    WHERE s.region = %s
      AND s.status = 'ACTIVE'
      AND sf.on_sale = true
      AND f.name = ANY(%s)
      AND f.active = true
      AND s.deleted_at IS NULL
    GROUP BY s.id, s.shop_name, s.address, s.district
    HAVING array_length(array_agg(DISTINCT f.name), 1) > 0
    ORDER BY match_count DESC, s.id
    LIMIT 3
"""

_SQL_BY_REGIONS = """
    SELECT
        s.id        AS shop_id,
        s.shop_name,
        s.address,
        s.region,
        s.district,
        array_agg(DISTINCT f.name)                     AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1)    AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers     f  ON f.id = sf.flower_id
    WHERE s.region = ANY(%s)
      AND s.status = 'ACTIVE'
      AND sf.on_sale = true
      AND f.name = ANY(%s)
      AND f.active = true
      AND s.deleted_at IS NULL
    GROUP BY s.id, s.shop_name, s.address, s.region, s.district
    HAVING array_length(array_agg(DISTINCT f.name), 1) > 0
    ORDER BY match_count DESC, s.id
    LIMIT 6
"""


def _rows_to_shops(rows) -> list:
    return [
        {
            "shopName":         r["shop_name"],
            "address":          r["address"],
            "district":         r["district"],
            "available_flowers": r["flower_names"],
        }
        for r in rows
    ]


def _is_district_code(code: str) -> bool:
    """'REGION_XXX' 형태인지 확인 (Region 코드는 언더스코어 없음)."""
    parts = code.split("_", 1)
    return len(parts) == 2 and parts[0] in REGION_CODES


@tool
def get_flowers_by_sentiment(sentiment_keywords: str) -> str:
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
    try:
        parts = location_and_flowers.split("|")
        if len(parts) != 2:
            return json.dumps(
                {"error": "입력 형식 오류. '지역코드|꽃이름1,꽃이름2' 형식으로 입력하세요."},
                ensure_ascii=False
            )
        location_raw = parts[0].strip()
        flower_names = [f.strip() for f in parts[1].split(",") if f.strip()]

        if _is_district_code(location_raw):
            return _search_by_district(location_raw, flower_names)
        elif location_raw in REGION_CODES:
            return _search_by_region(location_raw, flower_names)
        else:
            return json.dumps(
                {"error": f"'{location_raw}'은(는) 알 수 없는 지역 코드입니다.", "shops": []},
                ensure_ascii=False
            )
    except Exception as e:
        return json.dumps({"error": str(e), "shops": []}, ensure_ascii=False)


def _search_by_district(district_code: str, flower_names: list) -> str:
    """District 코드로 꽃집 검색 → 없으면 인접 구 단일 쿼리 fallback."""
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(_SQL_BY_DISTRICT, (district_code, flower_names))
            rows = cur.fetchall()

    if rows:
        return json.dumps(
            {"location": district_code, "location_type": "district",
             "shops": _rows_to_shops(rows), "count": len(rows)},
            ensure_ascii=False, indent=2
        )

    # ── fallback 1: 인접 구 (단일 쿼리) ──────────────────────────────────
    nearby_districts = NEARBY_DISTRICTS.get(district_code, [])
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
                    "message": f"'{district_code}'에는 해당 꽃을 보유한 꽃집이 없습니다.",
                    "nearby_alternatives": _rows_to_shops(nearby_rows),
                },
                ensure_ascii=False, indent=2
            )

    # ── fallback 2: 같은 region 전체 ────────────────────────────────────
    region_code = district_code.split("_", 1)[0]
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(_SQL_BY_REGION, (region_code, flower_names))
            region_rows = cur.fetchall()

    return json.dumps(
        {
            "location": district_code, "location_type": "district",
            "shops": [], "count": 0,
            "message": f"'{district_code}' 및 인근 구에 해당 꽃을 보유한 꽃집이 없습니다.",
            "nearby_alternatives": _rows_to_shops(region_rows),
        },
        ensure_ascii=False, indent=2
    )


def _search_by_region(region_code: str, flower_names: list) -> str:
    """Region 코드로 꽃집 검색 → 없으면 인접 region 단일 쿼리 fallback."""
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(_SQL_BY_REGION, (region_code, flower_names))
            rows = cur.fetchall()

    if rows:
        return json.dumps(
            {"location": region_code, "location_type": "region",
             "shops": _rows_to_shops(rows), "count": len(rows)},
            ensure_ascii=False, indent=2
        )

    # ── fallback: 인접 region 단일 쿼리 (N+1 제거) ───────────────────────
    nearby_codes = NEARBY_REGIONS.get(region_code, [])
    nearby_results = []
    if nearby_codes:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(_SQL_BY_REGIONS, (nearby_codes, flower_names))
                nearby_rows = cur.fetchall()

        # 지역별로 그룹핑 (최대 2개 지역, 각 3곳)
        seen_regions: dict = {}
        for r in nearby_rows:
            rc = r["region"]
            if rc not in seen_regions:
                seen_regions[rc] = []
            if len(seen_regions[rc]) < 3:
                seen_regions[rc].append({
                    "shopName":          r["shop_name"],
                    "address":           r["address"],
                    "district":          r["district"],
                    "available_flowers": r["flower_names"],
                })
            if len(seen_regions) >= 2 and all(len(v) >= 1 for v in seen_regions.values()):
                break

        nearby_results = [
            {"region": rc, "shops": shops}
            for rc, shops in seen_regions.items()
        ]

    return json.dumps(
        {
            "location": region_code, "location_type": "region",
            "shops": [], "count": 0,
            "message": f"'{region_code}'에는 해당 꽃을 보유한 꽃집이 없습니다.",
            "nearby_alternatives": nearby_results,
        },
        ensure_ascii=False, indent=2
    )
