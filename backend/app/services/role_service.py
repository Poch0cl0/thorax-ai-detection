"""Roles por usuario (`user_roles` + compatibilidad con `users.role`)."""

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserRole


class RoleService:
    @staticmethod
    def roles_for_user(db: Session, user_id: int) -> list[str]:
        rows = db.scalars(
            select(UserRole.role).where(UserRole.user_id == user_id).order_by(
                UserRole.role
            ),
        ).all()
        return sorted(set(rows))

    @staticmethod
    def add_roles_uncommitted(db: Session, user_id: int, roles: Iterable[str]) -> None:
        current = set(RoleService.roles_for_user(db, user_id))
        for role in roles:
            if role in current:
                continue
            db.add(UserRole(user_id=user_id, role=role))

    @staticmethod
    def sync_from_primary_role_uncommitted(db: Session, user_id: int, primary: str) -> None:
        RoleService.add_roles_uncommitted(db, user_id, [primary])

    @staticmethod
    def user_has_any(db: Session, user_id: int, roles: set[str]) -> bool:
        have = set(RoleService.roles_for_user(db, user_id))
        return bool(have.intersection(roles))

    @staticmethod
    def users_with_role(db: Session, role_name: str) -> list[User]:
        stmt = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .where(UserRole.role == role_name, User.is_active.is_(True))
            .order_by(User.email.asc())
        )
        return list(db.scalars(stmt).unique().all())
