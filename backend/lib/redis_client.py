"""
Conditional Redis client initialization based on environment.
Provides real Redis for production, MockRedis for development.
"""

from backend.config import settings
from backend.lib.cache import MockRedis

if settings.app_environment == "development":
    redis_client = MockRedis()
else:
    import redis

    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )
