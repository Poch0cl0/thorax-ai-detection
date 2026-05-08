from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.user import UserBriefRead, UserCreate, UserRead
from app.services.role_service import RoleService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    if UserService.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    user = UserService.create(db, data)
    return UserService.to_read(db, user)


@router.get("/me", response_model=UserRead)
def read_me(
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserService.to_read(db, current)


@router.get("/specialists-clinicians", response_model=list[UserBriefRead])
def list_specialist_clinicians(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[UserBriefRead]:
    clinicians = RoleService.users_with_role(db, "clinician")
    return [
        UserBriefRead(
            id=u.id,
            email=u.email,  # type: ignore[arg-type]
            full_name=u.full_name,
            roles=RoleService.roles_for_user(db, u.id),
        )
        for u in clinicians
    ]
