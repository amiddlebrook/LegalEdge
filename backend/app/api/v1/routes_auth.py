"""Authentication API endpoints."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.auth import User
from app.repositories.auth import get_user_by_email, get_user_by_username, update_user_last_login, create_user
from app.schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)
from app.services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_superuser,
    log_audit_event,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Register a new user account."""
    # Check if user already exists
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await get_user_by_username(session, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = await create_user(session, user_data)
    await session.commit()

    # Log audit event
    await log_audit_event(
        session=session,
        user=user,
        action="user.registered",
        resource="user",
        resource_id=str(user.id),
        details={"email": user.email, "username": user.username},
        request=request
    )

    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Token:
    """OAuth2 compatible token endpoint."""
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await update_user_last_login(session, user)

    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Log audit event
    await log_audit_event(
        session=session,
        user=user,
        action="user.login",
        resource="auth",
        details={"login_method": "password"},
        request=request
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    refresh_token: str,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Refresh an access token using a refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = await get_user_by_username(session, username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    # Log audit event
    await log_audit_event(
        session=session,
        user=user,
        action="token.refresh",
        resource="auth",
        request=request
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserRead:
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Update current user information."""
    # Update user fields
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.username is not None:
        current_user.username = user_update.username
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.preferences is not None:
        current_user.preferences.update(user_update.preferences)

    await session.commit()

    # Log audit event
    await log_audit_event(
        session=session,
        user=current_user,
        action="user.updated",
        resource="user",
        resource_id=str(current_user.id),
        details={"updated_fields": list(user_update.model_dump(exclude_unset=True).keys())},
        request=request
    )

    return current_user


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """Logout the current user."""
    await log_audit_event(
        session=session,
        user=current_user,
        action="user.logout",
        resource="auth",
        request=request
    )

    return {"message": "Successfully logged out"}
