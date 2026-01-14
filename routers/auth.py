from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status

from core.constants import Supabase
from core.security import get_auth_service
from schemas.auth import (
    AuthResponse,
    OAuthCallbackRequest,
    OAuthProvider,
    OAuthResponse,
    PasswordResetRequest,
    PasswordUpdateRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from schemas.common import ErrorResponseSchema
from services.auth_service import AuthService
from utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    responses={
        403: {"model": ErrorResponseSchema, "description": "Forbidden Response"}
    },
)


def handle_auth_error(e: Exception) -> HTTPException:
    """
    Convert auth errors to appropriate HTTP exceptions

    Args:
        e: Exception from auth operation

    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(e, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Authentication error: {e!s}",
    )


def format_auth_response(result: dict[str, Any]) -> AuthResponse:
    """
    Format Supabase auth result into standardized response

    Args:
        result: Raw result from Supabase auth operation

    Returns:
        Formatted auth response with user and token data
    """
    full_name = result["user"].get("full_name", "")
    if not full_name:
        user_metadata = result["user"]["user_metadata"]
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get(Supabase.FULL_NAME_FIELD, "")

    user_response = UserResponse(
        id=result["user"]["id"],
        email=result["user"]["email"],
        full_name=full_name,
        created_at=result["user"]["created_at"],
    )

    token_response = TokenResponse(
        access_token="",
        refresh_token="",
        token_type="bearer",
    )

    session_data = result.get("session")
    if (
        session_data
        and isinstance(session_data, dict)
        and session_data.get("access_token")
    ):
        token_response = TokenResponse(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"],
            token_type="bearer",
        )

    return AuthResponse(user=user_response, token=token_response)


@router.post(
    "/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        result = await auth_service.signup(user_data)
        return format_auth_response(result)
    except Exception as e:
        raise handle_auth_error(e) from e


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        result = await auth_service.login(user_data)
        return format_auth_response(result)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None
    except Exception as e:
        raise handle_auth_error(e) from e


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(TokenResponse),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    try:
        await auth_service.logout(token)
    except Exception as e:
        raise handle_auth_error(e) from e


@router.get("/google-login", response_model=OAuthResponse)
async def google_login(
    provider: OAuthProvider,
    redirect_url: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> OAuthResponse:
    try:
        auth_response = await auth_service.oauth_login(
            provider=provider, redirect_url=redirect_url
        )
        return OAuthResponse(auth_url=auth_response["auth_url"])
    except Exception as e:
        raise handle_auth_error(e)


@router.post("/callback", response_model=AuthResponse)
async def oauth_callback(
    data: OAuthCallbackRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        result = await auth_service.handle_oauth_callback(
            provider=data.provider,
            code=data.code,
            redirect_url=data.redirect_url,
        )
        return format_auth_response(result)
    except Exception as e:
        raise handle_auth_error(e)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    password_reset: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """Request password reset email"""
    try:
        # Include the redirect URL for the reset page
        redirect_url = f"{password_reset.redirect_url or 'http://localhost:3000'}/auth/reset-password"
        await auth_service.request_password_reset(password_reset.email, redirect_url)
        return {"detail": "Password reset email sent"}
    except Exception as e:
        logger.error("Password Reset Request Error", extra={"error": e})
        raise handle_auth_error(e) from e


@router.post("/update-password", status_code=status.HTTP_200_OK)
async def update_password(
    password_update: PasswordUpdateRequest,
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """Update password using access token from reset link"""
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        access_token = authorization.replace("Bearer ", "")

        await auth_service.update_password(
            access_token=access_token, new_password=password_update.new_password
        )

        return {"detail": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Password Update Error", extra={"error": e})
        raise handle_auth_error(e) from e
