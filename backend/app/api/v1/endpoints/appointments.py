from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models import User
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

SecretaryOrAdmin = Annotated[User, Depends(require_roles("secretaria", "admin"))]


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
    scheduled_from: datetime | None = Query(None),
    scheduled_to: datetime | None = Query(None),
) -> list:
    return AppointmentService.list_for_user(
        db,
        user_id=current.id,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
    )


@router.post(
    "",
    response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    data: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
    current: SecretaryOrAdmin,
) -> object:
    try:
        return AppointmentService.create(db, data, created_by_id=current.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> object:
    try:
        ap = AppointmentService.update(db, appointment_id, data, actor_id=current.id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not ap:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return ap


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current: SecretaryOrAdmin,
) -> None:
    try:
        ok = AppointmentService.delete_if_pending(
            db, appointment_id, actor_id=current.id
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not ok:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
