from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
# From: from fastapi.security import OAuth2PasswordRequestForm
from backend.src.api.v1.schemas.user_schemas import UserCreate # For login
from fastapi.security import HTTPAuthorizationCredentials # <-- New import

from sqlalchemy.orm import Session

from backend.src.database.database import get_db
from backend.src.database.models.user import User
from backend.src.api.v1.schemas.user_schemas import UserResponse, Token, TokenData
from backend.src.core.security import (
    create_access_token,
    verify_password,
    security_scheme, # <-- Use the new scheme
    verify_token
)
from backend.src.services import user_service
from backend.src.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency to get the current authenticated user
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)], # <-- Changed
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # The actual token string is in credentials.credentials
    token_data = verify_token(credentials.credentials, credentials_exception) # <-- Changed
    user = user_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Dependency to get the current active user (e.g., for protected endpoints)
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    # You can add checks for user activity status here if needed
    return current_user


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)

# Changed from /token to /login for clarity, and accepts JSON body
@router.post("/login", response_model=Token) # <-- Changed endpoint name
def login_for_access_token(
    user_credentials: UserCreate, # <-- Accepts Pydantic model (JSON body)
    db: Session = Depends(get_db)
):
    user = user_service.get_user_by_email(db, email=user_credentials.email) # <-- Changed
    if not user or not verify_password(user_credentials.password, user.hashed_password): # <-- Changed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password", # <-- Changed detail
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user