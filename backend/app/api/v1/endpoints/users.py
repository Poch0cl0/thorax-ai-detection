from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if UserService.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    return UserService.create(db, data)


@router.get("/me", response_model=UserRead)
def read_me(
    current: Annotated[User, Depends(get_current_user)],
) -> User:
    return current
