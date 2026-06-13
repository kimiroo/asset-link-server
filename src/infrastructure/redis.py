from redis.asyncio import Redis

from src.core.config import get_settings
from src.core.const import REDIS_AUTH_CACHE_DB, REDIS_SESSION_DB


settings = get_settings()

auth_cache_redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=REDIS_AUTH_CACHE_DB,
    decode_responses=True
)

user_session_redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=REDIS_SESSION_DB,
    decode_responses=True
)