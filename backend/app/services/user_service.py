from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserRead
from app.services.role_service import RoleService


class UserService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, data: UserCreate) -> User:
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role,
        )
        db.add(user)
        db.flush()
        RoleService.sync_from_primary_role_uncommitted(db, user.id, data.role)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def to_read(db: Session, user: User) -> UserRead:
        roles = RoleService.roles_for_user(db, user.id)
        if not roles:
            roles = [user.role]
        return UserRead(
            id=user.id,
            email=user.email,  # type: ignore[arg-type]
            full_name=user.full_name,
            is_active=user.is_active,
            role=user.role,
            roles=roles,
            created_at=user.created_at,
        )

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        user = UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
