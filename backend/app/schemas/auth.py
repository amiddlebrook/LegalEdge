"""Authentication and authorization schemas."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    """OAuth 2.0 token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class TokenData(BaseModel):
    """Token payload data."""

    sub: str | None = None
    exp: datetime | None = None
    scopes: List[str] = []


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=256)
    is_active: bool = True
    is_superuser: bool = False

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('username must be alphanumeric with underscores or hyphens')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    preferences: Dict[str, Any] | None = None


class UserRead(UserBase):
    """Schema for reading user information."""

    id: int
    provider: str | None = None
    avatar_url: str | None = None
    preferences: Dict[str, Any] = {}
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class OAuthProvider(BaseModel):
    """OAuth provider configuration."""

    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: List[str] = ["openid", "profile", "email"]


class OAuthCallback(BaseModel):
    """OAuth callback data."""

    code: str
    state: str | None = None


class Permission(BaseModel):
    """Individual permission."""

    resource: str
    action: str
    conditions: Dict[str, Any] | None = None


class RoleBase(BaseModel):
    """Base role schema."""

    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1, max_length=256)
    permissions: Dict[str, Any] = {}


class RoleCreate(RoleBase):
    """Schema for creating a role."""

    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""

    name: str | None = None
    description: str | None = None
    permissions: Dict[str, Any] | None = None


class RoleRead(RoleBase):
    """Schema for reading role information."""

    id: int
    created_at: datetime
    updated_at: datetime


class UserRoleCreate(BaseModel):
    """Schema for assigning a role to a user."""

    user_id: int
    role_id: int


class UserRoleRead(BaseModel):
    """Schema for reading user-role associations."""

    id: int
    user_id: int
    role_id: int
    created_at: datetime
    role: RoleRead | None = None


class AuditLogCreate(BaseModel):
    """Schema for creating audit logs."""

    action: str
    resource: str
    resource_id: str | None = None
    details: Dict[str, Any] = {}


class AuditLogRead(AuditLogCreate):
    """Schema for reading audit logs."""

    id: int
    user_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    method: str | None = None
    path: str | None = None
    created_at: datetime


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
