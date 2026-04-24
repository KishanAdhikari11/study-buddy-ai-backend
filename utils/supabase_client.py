import asyncio
import time

from supabase import Client, create_client
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from core.settings import settings

_supabase_client: Client | None = None
_client_created_at: float = 0
_CLIENT_TTL: float = 400


def _is_transient(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(x in msg for x in ["timeout", "connection", "503", "502", "500"])


def get_supabase_client() -> Client:
    global _supabase_client, _client_created_at
    if (
        _supabase_client is None
        or (time.monotonic() - _client_created_at) > _CLIENT_TTL
    ):
        _supabase_client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
        _client_created_at = time.monotonic()
    return _supabase_client


@retry(
    retry=retry_if_exception(_is_transient),
    wait=wait_exponential(multiplier=2, min=4, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get_signed_url(path: str, expires_in: int = 3600) -> str:
    supabase = get_supabase_client()
    response = supabase.storage.from_(settings.SUPABASE_BUCKET).create_signed_url(
        path=path, expires_in=expires_in
    )
    if "signedURL" not in response:
        raise Exception("Signed URL not found in response")
    return response["signedURL"]


async def get_signed_url(path: str, expires_in: int = 3600) -> str:
    return await asyncio.to_thread(_get_signed_url, path, expires_in)
