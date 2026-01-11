from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from core.constants import OAuth, Validation


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(..., min_length=Validation.MIN_PASSWORD_LENGTH)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserLogin(UserBase):
    """User login schema"""

    password: str


class UserResponse(UserBase):
    """User response schema"""

    id: str
    full_name: str
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Authentication response schema"""

    user: UserResponse
    token: TokenResponse


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr
    redirect_url: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "redirect_url": "http://localhost:3000",
            }
        }


class PasswordUpdateRequest(BaseModel):
    """Schema for updating password with reset token"""

    new_password: str = Field(
        ..., min_length=Validation.MIN_PASSWORD_LENGTH, description="New password"
    )

    class Config:
        json_schema_extra = {"example": {"new_password": "NewSecurePassword123!"}}


class OAuthProvider(str, Enum):
    """OAuth provider options"""

    GOOGLE = OAuth.GOOGLE


class OAuthLoginRequest(BaseModel):
    """OAuth login initiation request"""

    provider: OAuthProvider
    redirect_url: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""

    provider: OAuthProvider
    code: str
    redirect_url: str


class OAuthResponse(BaseModel):
    """OAuth login response"""

    auth_url: str
