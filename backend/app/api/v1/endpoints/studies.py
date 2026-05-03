from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.study import StudyCreate, StudyRead, StudyUpdate
from app.services.study_service import StudyService

router = APIRouter(prefix="/studies", tags=["studies"])


@router.post("", response_model=StudyRead, status_code=status.HTTP_201_CREATED)
def create_study(
    data: StudyCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    return StudyService.create(db, data)


@router.get("/{study_id}", response_model=StudyRead)
def get_study(
    study_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    s = StudyService.get(db, study_id)
    if not s:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return s


@router.get("/patient/{patient_id}", response_model=list[StudyRead])
def list_by_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list:
    return StudyService.list_for_patient(db, patient_id)


@router.patch("/{study_id}", response_model=StudyRead)
def update_study(
    study_id: int,
    data: StudyUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    s = StudyService.update(db, study_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return s
