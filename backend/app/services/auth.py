"""Authentication and authorization services."""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth import AuditLog, Role, User, UserRole
from app.repositories.auth import (
    create_audit_log,
    create_role,
    create_user,
    create_user_role,
    get_role_by_name,
    get_user_by_email,
    get_user_by_username,
    get_user_roles,
    update_user_last_login,
)
from app.schemas.auth import (
    AuditLogCreate,
    OAuthCallback,
    OAuthProvider,
    Permission,
    RoleCreate,
    Token,
    TokenData,
    UserCreate,
    UserLogin,
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# JWT configuration
SECRET_KEY = settings.openai_api_key or "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting
rate_limit_storage = {}  # In production, use Redis


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    """Authenticate a user with username and password."""
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: AsyncSession,
    token: str | None = None,
    required_scopes: List[str] | None = None
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(sub=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(session, username=token_data.sub)
    if user is None:
        raise credentials_exception

    # Check scopes if required
    if required_scopes:
        user_scopes = await get_user_scopes(session, user.id)
        if not all(scope in user_scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    return user


async def get_current_active_user(current_user: User = None) -> User:
    """Get the current active user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = None) -> User:
    """Get the current superuser."""
    current_user = await get_current_active_user(current_user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_user_scopes(session: AsyncSession, user_id: int) -> List[str]:
    """Get all scopes for a user based on their roles."""
    roles = await get_user_roles(session, user_id)
    scopes = []

    for user_role in roles:
        role_scopes = user_role.role.permissions.get("scopes", [])
        scopes.extend(role_scopes)

    return list(set(scopes))  # Remove duplicates


def check_rate_limit(identifier: str, config: dict) -> bool:
    """Check if a request should be rate limited."""
    now = datetime.now(timezone.utc)
    key = f"rate_limit:{identifier}"

    # Clean up old entries
    cutoff = now - timedelta(hours=1)
    to_remove = []
    for k in rate_limit_storage:
        if k.startswith("rate_limit:") and rate_limit_storage[k]["last_reset"] < cutoff:
            to_remove.append(k)
    for k in to_remove:
        del rate_limit_storage[k]

    # Check rate limit
    if key not in rate_limit_storage:
        rate_limit_storage[key] = {
            "count": 1,
            "last_reset": now,
            "requests": [now.timestamp()]
        }
        return True

    entry = rate_limit_storage[key]
    window_start = now - timedelta(minutes=1)

    # Clean old requests from the window
    entry["requests"] = [ts for ts in entry["requests"] if ts > window_start.timestamp()]

    # Check if under limit
    if len(entry["requests"]) < config.get("requests_per_minute", 60):
        entry["requests"].append(now.timestamp())
        entry["count"] = len(entry["requests"])
        return True

    return False


async def log_audit_event(
    session: AsyncSession,
    user: User | None,
    action: str,
    resource: str,
    resource_id: str | None = None,
    details: dict | None = None,
    request: Request | None = None
) -> None:
    """Log an audit event."""
    audit_data = AuditLogCreate(
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details or {}
    )

    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=audit_data.action,
        resource=audit_data.resource,
        resource_id=audit_data.resource_id,
        details=audit_data.details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        method=request.method if request else None,
        path=request.url.path if request else None
    )

    await create_audit_log(session, audit_log)


async def create_default_roles(session: AsyncSession) -> None:
    """Create default roles with permissions."""
    roles_data = [
        {
            "name": "admin",
            "description": "Full system access",
            "permissions": {
                "scopes": ["read", "write", "admin", "audit"],
                "resources": {
                    "users": ["create", "read", "update", "delete"],
                    "alerts": ["create", "read", "update", "delete"],
                    "legislation": ["read", "update"],
                    "portfolio": ["read", "update"]
                }
            }
        },
        {
            "name": "analyst",
            "description": "Data analysis and insights access",
            "permissions": {
                "scopes": ["read", "write"],
                "resources": {
                    "alerts": ["read", "create"],
                    "legislation": ["read"],
                    "portfolio": ["read"],
                    "forecasting": ["read"]
                }
            }
        },
        {
            "name": "investor",
            "description": "Portfolio and market insights access",
            "permissions": {
                "scopes": ["read"],
                "resources": {
                    "alerts": ["read"],
                    "portfolio": ["read"],
                    "opportunities": ["read"]
                }
            }
        }
    ]

    for role_data in roles_data:
        existing_role = await get_role_by_name(session, role_data["name"])
        if not existing_role:
            role_create = RoleCreate(**role_data)
            await create_role(session, role_create)


async def initialize_auth_system(session: AsyncSession) -> None:
    """Initialize the authentication system with default roles."""
    await create_default_roles(session)
    logger.info("Authentication system initialized with default roles")
