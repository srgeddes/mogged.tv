from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from core.exceptions import AlreadyExistsError, ValidationError
from users.dependencies import get_user_repository
from users.repository import UserRepository

from . import service
from .dependencies import get_current_user
from .exceptions import InvalidCredentialsError
from .schemas import AuthResponse, LoginRequest, SignupRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthResponse:
    try:
        token, user = await service.signup(
            repo,
            username=body.username,
            email=body.email,
            password=body.password,
            display_name=body.display_name,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc

    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthResponse:
    try:
        token, user = await service.login(repo, email=body.email, password=body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc

    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(
    user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(user)
