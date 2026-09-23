from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from chat.models import User
from chat.repositories.user import UserRepository
from chat.routes.dependencies import get_user_repo, get_current_user
from chat.schemas.user import UserResponse, UserCreate, LoginResponse, Login, RefreshRequest
from chat.security import hash_password, create_access_token, verify_password, create_refresh_token, \
    decode_access_token, decode_refresh_token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
        user_data: UserCreate,
        user_repo: UserRepository = Depends(get_user_repo)
):
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    password_hash = hash_password(user_data.password)
    user = user_repo.create(
        email=user_data.email,
        password_hash=password_hash
    )
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
        user_data: Login,
        user_repo: UserRepository = Depends(get_user_repo)
):
    user = await user_repo.get_by_email(user_data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(data: RefreshRequest):
    try:
        user_id = decode_refresh_token(data.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(user_id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,
    )



@router.get("/me", response_model=UserResponse)
async def me(
        current_user: User = Depends(get_current_user)
) -> User:
    return current_user
