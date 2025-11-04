from utils.constants import OAuth, Supabase
from typing import Any
from utils.logger import get_logger
from utils.supabase_client import get_supabase_client
from schemas.auth import UserCreate,UserLogin

logger =get_logger()


class AuthService:
    """Services for authentication operations """
    def __init__(self) -> None:
        self.client=get_supabase_client()
        
    async def login(self,user_data:UserCreate ) ->dict[str,Any]:
        try:
            auth_response= self.client.auth.sign_up(
                {
                    "email":user_data.email,
                    "password":user_data.password,
                    "options":{
                        "data": {
                            Supabase.FULL_NAME_FIELD: user_data.full_name,
                        }
                    },
                }
            )
            if not hasattr(auth_response, "user") or not auth_response.user:
                raise ValueError(
                    f"Registration failed: Could not create user"
                )

            logger.info("User Created Successfully",extra={"user":user_data.full_name})

            return self._build_auth_dict(auth_response)
        except Exception as e:
            logger.error(f"Signup error: {e!s}")
            raise ValueError(f"Registration failed: {e!s}") from e

       
    def _build_auth_dict(self, auth_response: Any) -> dict[str, Any]:
        """Build auth dict in format expected by format_auth_response helper"""
        user_metadata = auth_response.user.user_metadata
        if isinstance(user_metadata, str):
            logger.warning(f"User metadata is string instead of dict: {user_metadata}")
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