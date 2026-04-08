_SQL_BY_DISTRICT = """
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

_SQL_BY_DISTRICT_WITH_ADDR = """
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
    WHERE s.district = %s
      AND s.status = 'ACTIVE'
      AND sf.on_sale = true
      AND f.name = ANY(%s)
      AND f.active = true
      AND s.deleted_at IS NULL
      AND s.address ILIKE %s
    GROUP BY s.id, s.shop_name, s.address, s.district
    HAVING array_length(array_agg(DISTINCT f.name), 1) > 0
    ORDER BY match_count DESC, s.id
    LIMIT 3
"""

_SQL_BY_DISTRICTS = """
    SELECT
        s.id AS shop_id,
        s.shop_name,
        s.address,
        s.district,
        array_agg(DISTINCT f.name)  AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1) AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers f ON f.id = sf.flower_id
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

_SQL_BY_REGIONS = """
    SELECT
        s.id AS shop_id,
        s.shop_name,
        s.address,
        s.region,
        s.district,
        array_agg(DISTINCT f.name) AS flower_names,
        array_length(array_agg(DISTINCT f.name), 1) AS match_count
    FROM shops s
    JOIN shop_flowers sf ON sf.shop_id = s.id
    JOIN flowers f ON f.id = sf.flower_id
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