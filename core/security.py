from utils.logger import get_logger
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from services.auth_services import AuthService

from core.settings import settings

logger = get_logger()

security_scheme = HTTPBearer()


def validate_jwt_token(token: str) -> str:
    """
    Extracts and validates the JWT token, return user_id

    Args:
        token (str): The JWT token to validate.

    Returns:
        user_id (str): The user ID extracted from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require_exp": True,
                "verify_aud": False,
            },
            audience="authenticated",
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing 'sub' field",
            )
        return str(user_id)
    except JWTError as e:
        logger.error("JWT validation error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    token = credentials.credentials
    return validate_jwt_token(token)


def get_auth_service() -> AuthService:
    return AuthService()
