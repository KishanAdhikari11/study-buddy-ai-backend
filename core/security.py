from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.settings import settings
from services.auth_services import AuthService
from utils.logger import get_logger

logger = get_logger()
security_scheme = HTTPBearer()


def validate_jwt_token(token: str) -> str:
    """
    Extracts and validates the JWT token, returns user_id.

    Args:
        token (str): The JWT token to validate.

    Returns:
        str: The user ID extracted from the token.

    Raises:
        HTTPException: If the token is invalid, expired, or missing 'sub'.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,
            },
            audience="authenticated",
        )

        sub = payload.get("sub")
        if sub is None or not isinstance(sub, str):
            logger.warning(
                "JWT missing or invalid 'sub' field",
                extra={"payload_keys": list(payload.keys())},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing or invalid 'sub' field",
            )

        return sub

    except JWTError as e:
        logger.error("JWT validation error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """Dependency to get current authenticated user ID."""
    return validate_jwt_token(credentials.credentials)


def get_auth_service() -> AuthService:
    """Dependency factory for AuthService."""
    return AuthService()
