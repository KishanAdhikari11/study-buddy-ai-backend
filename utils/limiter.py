from slowapi import Limiter
from slowapi.util import get_remote_address
from core.settings import settings

API_RATE_LIMIT = "5/minute"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[API_RATE_LIMIT],
)
