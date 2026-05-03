from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientRead])
def list_patients(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> list:
    return PatientService.list_all(db, skip=skip, limit=limit)


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    return PatientService.create(db, data)


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    p = PatientService.get(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return p


@router.patch("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    p = PatientService.update(db, patient_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return p
