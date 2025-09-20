"""Authentication repository functions."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import AuditLog, Role, User, UserRole
from app.schemas.auth import RoleCreate, UserCreate
from app.services.auth import get_password_hash


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Get a user by username."""
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Get a user by email."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        preferences=user_data.preferences or {}
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def update_user_last_login(session: AsyncSession, user: User) -> None:
    """Update user's last login timestamp."""
    user.last_login = datetime.now(timezone.utc)
    await session.flush()


async def get_role_by_name(session: AsyncSession, name: str) -> Role | None:
    """Get a role by name."""
    result = await session.execute(
        select(Role).where(Role.name == name)
    )
    return result.scalar_one_or_none()


async def create_role(session: AsyncSession, role_data: RoleCreate) -> Role:
    """Create a new role."""
    role = Role(
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions
    )
    session.add(role)
    await session.flush()
    await session.refresh(role)
    return role


async def get_user_roles(session: AsyncSession, user_id: int) -> List[UserRole]:
    """Get all roles for a user."""
    result = await session.execute(
        select(UserRole).where(UserRole.user_id == user_id)
    )
    return list(result.scalars().all())


async def create_user_role(session: AsyncSession, user_id: int, role_id: int) -> UserRole:
    """Create a user-role association."""
    user_role = UserRole(user_id=user_id, role_id=role_id)
    session.add(user_role)
    await session.flush()
    await session.refresh(user_role)
    return user_role


async def create_audit_log(session: AsyncSession, audit_log: AuditLog) -> AuditLog:
    """Create an audit log entry."""
    session.add(audit_log)
    await session.flush()
    await session.refresh(audit_log)
    return audit_log


async def get_audit_logs(
    session: AsyncSession,
    *,
    user_id: int | None = None,
    action: str | None = None,
    resource: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """Get audit logs with optional filters."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource:
        query = query.where(AuditLog.resource == resource)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())
