from typing import Any

from core.constants import OAuth, Supabase
from schemas.auth import UserCreate, UserLogin
from utils.logger import get_logger
from utils.supabase_client import get_supabase_client

logger = get_logger()


class AuthService:
    """Services for authentication operations"""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    async def signup(self, user_data: UserCreate) -> dict[str, Any]:
        try:
            auth_response = self.client.auth.sign_up(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                    "options": {
                        "data": {
                            "full_name": f"{user_data.first_name} {user_data.last_name}",
                        }
                    },
                }
            )

            if auth_response.user:
                logger.info("User Created", extra={"email": user_data.email})
                return self._build_auth_dict(auth_response)

            raise ValueError("Registration failed: No user data returned.")

        except Exception as e:
            error_msg = str(e).lower()
            if "already registered" in error_msg or "user_already_exists" in error_msg:
                raise ValueError("This email is already registered. Please log in.")

            logger.error("Signup error", exc_info=e)
            raise ValueError(f"Registration failed: {e!s}")

    async def login(self, user_data: UserLogin) -> dict[str, Any]:
        """Authenticate a user with email and password"""
        try:
            auth_response = self.client.auth.sign_in_with_password(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                }
            )
            if (
                not hasattr(auth_response, "user")
                or not auth_response.user
                or not auth_response.session
            ):
                raise ValueError("Error Authentication failed")

            logger.info(
                "User login successful", extra={"user_id": auth_response.user.id}
            )
            return self._build_auth_dict(auth_response)
        except Exception as e:
            logger.error("Login error:", extra={"error": e})
            raise ValueError("Authentication failed")

    async def logout(self, token: str) -> bool:
        try:
            self.client.auth.sign_out()
            logger.info("user logged out")
            return True
        except Exception as e:
            logger.error("logout error", extra={"error": e})
            return False

    async def request_password_reset(self, email: str, redirect_url: str) -> bool:
        """Send password reset email with redirect URL"""
        try:
            self.client.auth.reset_password_email(
                email, options={"redirect_to": redirect_url}
            )
            logger.info("Password reset email sent", extra={"email": email})
            return True
        except Exception as e:
            logger.error("Password reset request error", extra={"error": e})
            raise ValueError(f"Failed to send password reset email: {e!s}") from e

    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password using the access token from reset link"""
        try:
            self.client.auth.set_session(access_token, "")

            response = self.client.auth.update_user({"password": new_password})

            if not response.user:
                raise ValueError("Failed to update password")

            logger.info(
                "Password updated successfully", extra={"user_id": response.user.id}
            )
            return True

        except Exception as e:
            logger.error("Password update error", extra={"error": e})
            raise ValueError(f"Failed to update password: {e!s}") from e

    async def oauth_login(self, provider: str, redirect_url: str) -> dict[str, Any]:
        """Initiate OAuth login flow"""
        if provider != OAuth.GOOGLE:
            raise ValueError(f"Unsupported provider: {provider}")
        auth_response = self.client.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": redirect_url}}
        )

        return {"auth_url": auth_response.url}

    async def handle_oauth_callback(
        self, provider: str, code: str, redirect_url: str
    ) -> dict[str, Any]:
        """Handle OAuth callback - let Supabase handle PKCE code exchange"""
        if provider != OAuth.GOOGLE:
            raise ValueError(f"Unsupported provider: {provider}")

        try:
            code_exchange_params = {"auth_code": code, "redirect_to": redirect_url}

            auth_response = self.client.auth.exchange_code_for_session(
                code_exchange_params  # type: ignore
            )

            if not auth_response.user or not auth_response.session:
                raise ValueError("Failed to exchange code for session")

            logger.info(
                "OAuth login successful", extra={"user_id": auth_response.user.id}
            )
            return self._build_auth_dict(auth_response)

        except Exception as e:
            logger.error("OAuth authentication error", extra={"error": e})
            raise ValueError(f"OAuth authentication failed: {e!s}") from e

    def _build_auth_dict(self, auth_response: Any) -> dict[str, Any]:
        """Build auth dict in format expected by format_auth_response helper"""
        user_metadata = auth_response.user.user_metadata
        if isinstance(user_metadata, str):
            logger.warning(
                "User metadata is string instead of dict",
                extra={"user_metadata": user_metadata},
            )
            user_metadata = {}
        elif user_metadata is None:
            user_metadata = {}

        full_name = ""
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get(Supabase.FULL_NAME_FIELD, "")

        user_dict = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "user_metadata": user_metadata,
            "full_name": full_name,
            "created_at": auth_response.user.created_at,
        }

        session_dict = {}
        if auth_response.session:
            session_obj = auth_response.session
            access_token = getattr(session_obj, "access_token", None)
            refresh_token = getattr(session_obj, "refresh_token", None)

            if access_token:
                session_dict = {
                    "access_token": access_token,
                    "refresh_token": refresh_token or "",
                }

        return {
            "user": user_dict,
            "session": session_dict,
        }
