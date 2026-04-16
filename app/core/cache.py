import json
import redis
from app.core.config import REDIS_CONFIG

_client: redis.Redis | None = None
_SHOP_TTL = 1209600


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(
            **REDIS_CONFIG,
            decode_responses=True,
            socket_connect_timeout=2,
        )
    return _client


def _shop_key(location_code: str, flower_names: list[str]) -> str:
    flowers = ",".join(sorted(flower_names))
    return f"flowerable:shops:{location_code}:{flowers}"


def get_cached_shops(location_code: str, flower_names: list[str]) -> list[dict] | None:
    """캐시 히트 시 전체 shop 리스트 반환, 미스 또는 Redis 장애 시 None."""
    try:
        raw = _get_client().get(_shop_key(location_code, flower_names))
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def set_cached_shops(location_code: str, flower_names: list[str], shops: list[dict]) -> None:
    """전체 shop 리스트를 TTL 1시간으로 캐싱. Redis 장애 시 무시."""
    try:
        _get_client().setex(
            _shop_key(location_code, flower_names),
            _SHOP_TTL,
            json.dumps(shops, ensure_ascii=False),
        )
    except Exception:
        pass
