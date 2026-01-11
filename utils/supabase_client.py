import asyncio

from supabase import Client, create_client
from tenacity import retry, stop_after_attempt, wait_exponential

from core.settings import settings

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
    return _supabase_client


@retry(
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
