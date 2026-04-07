"""
Flowerable CrewAI - DB Tools
PostgreSQL 연동 CrewAI 도구 모음
Tables: flowers, shops, shop_flowers, shop_flower_colors
"""
import os
import json
import psycopg2
import psycopg2.extras
from crewai.tools import tool

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Region 한글 → DB Enum 매핑
REGION_MAP = {
    "서울": "SEOUL", "경기": "GYEONGGI", "강원": "GANGWON",
    "광주": "GWANGJU", "인천": "INCHEON", "대구": "DAEGU",
    "부산": "BUSAN", "대전": "DAEJEON", "울산": "ULSAN",
    "세종": "SEJONG", "충북": "CHUNGBUK", "충청북도": "CHUNGBUK",
    "충남": "CHUNGNAM", "충청남도": "CHUNGNAM",
    "전북": "JEONBUK", "전라북도": "JEONBUK",
    "전남": "JEONNAM", "전라남도": "JEONNAM",
    "경북": "GYEONGBUK", "경상북도": "GYEONGBUK",
    "경남": "GYEONGNAM", "경상남도": "GYEONGNAM",
    "제주": "JEJU",
    "서울특별시": "SEOUL", "경기도": "GYEONGGI",
    "강원특별자치도": "GANGWON", "광주광역시": "GWANGJU",
    "인천광역시": "INCHEON", "대구광역시": "DAEGU",
    "부산광역시": "BUSAN", "대전광역시": "DAEJEON",
    "울산광역시": "ULSAN", "세종특별자치시": "SEJONG",
    "제주특별자치도": "JEJU",
}

# 인접 지역 매핑 (꽃집 없을 때 대안 제시용)
NEARBY_REGIONS = {
    "SEOUL": ["GYEONGGI", "INCHEON"],
    "GYEONGGI": ["SEOUL", "INCHEON", "GANGWON", "CHUNGNAM", "CHUNGBUK"],
    "INCHEON": ["SEOUL", "GYEONGGI"],
    "GANGWON": ["GYEONGGI", "CHUNGBUK", "GYEONGBUK"],
    "DAEJEON": ["CHUNGNAM", "CHUNGBUK", "GYEONGBUK", "GYEONGNAM"],
    "CHUNGBUK": ["GYEONGGI", "GANGWON", "DAEJEON", "CHUNGNAM"],
    "CHUNGNAM": ["GYEONGGI", "DAEJEON", "CHUNGBUK", "JEONBUK"],
    "GWANGJU": ["JEONNAM", "JEONBUK"],
    "JEONBUK": ["CHUNGNAM", "GWANGJU", "JEONNAM", "GYEONGNAM"],
    "JEONNAM": ["GWANGJU", "JEONBUK", "GYEONGNAM"],
    "DAEGU": ["GYEONGBUK", "GYEONGNAM"],
    "GYEONGBUK": ["DAEGU", "GANGWON", "CHUNGBUK", "GYEONGNAM"],
    "GYEONGNAM": ["DAEGU", "BUSAN", "ULSAN", "JEONNAM"],
    "BUSAN": ["GYEONGNAM", "ULSAN"],
    "ULSAN": ["BUSAN", "GYEONGNAM", "GYEONGBUK"],
    "SEJONG": ["DAEJEON", "CHUNGNAM", "CHUNGBUK"],
    "JEJU": [],
}


def _get_conn():
    return psycopg2.connect(**DB_CONFIG)


@tool
def get_flowers_by_sentiment(sentiment_keywords: str) -> str:
    """
    감정/상황 키워드를 기반으로 DB에 등록된 꽃 목록을 조회합니다.
    입력: 상황에서 추출된 감정 키워드 (예: '사랑,고백', '축하,기쁨', '사과,미안')
    반환: id, name, floralLang, category가 포함된 꽃 목록 (JSON)
    주의: 이 도구가 반환한 꽃 목록 외에는 절대 추천하지 마세요.
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
        return json.dumps(
            {"flowers": flowers, "total": len(flowers)},
            ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps({"error": str(e), "flowers": []}, ensure_ascii=False)


@tool
def get_matching_sub_flowers(main_flower_name: str) -> str:
    """
    선정된 메인 꽃과 조합 가능한 서브 꽃 및 필러 소재를 DB에서 조회합니다.
    입력: 메인 꽃 이름 (예: '장미', '튤립')
    반환: 메인 꽃을 제외한 나머지 활성화 꽃 목록 - Bouquet Stylist가 시각적 조화를 고려해 선택
    주의: 이 도구가 반환한 목록에서만 서브 꽃을 선택하세요.
    """
    filler_names = ["안개꽃", "팜파스", "목화", "수국", "소국", "스위트피", "리시안셔스"]

    sql_main = "SELECT id FROM flowers WHERE name = %s AND active = true"
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
                cur.execute(sql_main, (main_flower_name,))
                main_row = cur.fetchone()
                if not main_row:
                    return json.dumps(
                        {"error": f"'{main_flower_name}' 꽃이 DB에 존재하지 않습니다.", "flowers": []},
                        ensure_ascii=False
                    )
                cur.execute(sql_others, (filler_names, main_flower_name, filler_names))
                rows = cur.fetchall()
        flowers = [
            {"id": r["id"], "name": r["name"],
             "floralLang": r["floral_lang"], "category": r["category"], "role": r["role"]}
            for r in rows
        ]
        return json.dumps(
            {"main_flower": main_flower_name, "candidates": flowers, "total": len(flowers)},
            ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps({"error": str(e), "flowers": []}, ensure_ascii=False)


@tool
def get_shops_by_location_and_flower(location_and_flowers: str) -> str:
    """
    특정 지역에서 해당 꽃을 보유한 ACTIVE 꽃집을 DB에서 조회합니다.
    입력 형식: "지역명|꽃이름1,꽃이름2" (예: "서울|장미,튤립")
    반환: 꽃집 이름, 주소, 구, 보유 꽃 목록 (최대 3곳)
    꽃집이 없는 경우 인접 지역 정보도 함께 반환합니다.
    """
    try:
        parts = location_and_flowers.split("|")
        if len(parts) != 2:
            return json.dumps(
                {"error": "입력 형식 오류. '지역명|꽃이름1,꽃이름2' 형식으로 입력하세요."},
                ensure_ascii=False
            )
        location_raw = parts[0].strip()
        flower_names = [f.strip() for f in parts[1].split(",") if f.strip()]

        region_code = REGION_MAP.get(location_raw)
        if not region_code:
            return json.dumps(
                {"error": f"'{location_raw}'은(는) 지원하지 않는 지역입니다.", "shops": []},
                ensure_ascii=False
            )

        sql = """
            SELECT
                s.id AS shop_id,
                s.shop_name,
                s.address,
                s.district,
                array_agg(DISTINCT f.name) AS flower_names,
                array_length(array_agg(DISTINCT f.name), 1) AS match_count
            FROM shops s
            JOIN shop_flowers sf ON sf.shop_id = s.id
            JOIN flowers f ON f.id = sf.flower_id
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
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (region_code, flower_names))
                rows = cur.fetchall()

        if rows:
            shops = [
                {
                    "shopName": r["shop_name"],
                    "address": r["address"],
                    "district": r["district"],
                    "available_flowers": r["flower_names"],
                }
                for r in rows
            ]
            return json.dumps(
                {"region": location_raw, "shops": shops, "count": len(shops)},
                ensure_ascii=False, indent=2
            )

        # 꽃집 없을 때 - 인접 지역 조회
        nearby_codes = NEARBY_REGIONS.get(region_code, [])
        nearby_results = []
        for nearby_code in nearby_codes:
            with _get_conn() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(sql, (nearby_code, flower_names))
                    nr = cur.fetchall()
            if nr:
                region_label = next(
                    (k for k, v in REGION_MAP.items() if v == nearby_code and len(k) > 2), nearby_code
                )
                nearby_results.append({
                    "region": region_label,
                    "shops": [
                        {
                            "shopName": r["shop_name"],
                            "address": r["address"],
                            "district": r["district"],
                            "available_flowers": r["flower_names"],
                        }
                        for r in nr[:3]
                    ]
                })
            if len(nearby_results) >= 2:
                break

        return json.dumps(
            {
                "region": location_raw,
                "shops": [],
                "count": 0,
                "message": f"'{location_raw}'에는 해당 꽃을 보유한 꽃집이 없습니다.",
                "nearby_alternatives": nearby_results,
            },
            ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps({"error": str(e), "shops": []}, ensure_ascii=False)
