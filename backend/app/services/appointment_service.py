from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Appointment, Patient, User
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.role_service import RoleService


class AppointmentService:
    ROLES_CREATE = {"secretaria", "admin"}
    ROLES_CLINICIAN = {"clinician"}
    ROLES_VIEW_ALL = {"secretaria", "admin"}

    @staticmethod
    def _role_set(db: Session, user_id: int) -> set[str]:
        return set(RoleService.roles_for_user(db, user_id))

    @staticmethod
    def _select_visible(user_id: int, role_names: set[str]):
        stmt = select(Appointment).order_by(Appointment.scheduled_at.desc())
        if role_names.intersection(AppointmentService.ROLES_VIEW_ALL):
            return stmt
        return stmt.where(Appointment.attending_user_id == user_id)

    @staticmethod
    def list_for_user(
        db: Session,
        *,
        user_id: int,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
    ) -> list[Appointment]:
        roles = AppointmentService._role_set(db, user_id)
        stmt = AppointmentService._select_visible(user_id, roles)
        if scheduled_from is not None:
            stmt = stmt.where(Appointment.scheduled_at >= scheduled_from)
        if scheduled_to is not None:
            stmt = stmt.where(Appointment.scheduled_at <= scheduled_to)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get(db: Session, appt_id: int) -> Appointment | None:
        return db.get(Appointment, appt_id)

    @staticmethod
    def create(
        db: Session,
        data: AppointmentCreate,
        *,
        created_by_id: int,
    ) -> Appointment:
        patient = db.get(Patient, data.patient_id)
        if not patient:
            raise ValueError("Paciente no encontrado")
        doctor = db.get(User, data.attending_user_id)
        if not doctor:
            raise ValueError("Médico asignado no encontrado")
        if not RoleService.user_has_any(
            db, data.attending_user_id, AppointmentService.ROLES_CLINICIAN
        ):
            raise ValueError("El usuario asignado debe tener rol clinician")

        ap = Appointment(
            patient_id=data.patient_id,
            attending_user_id=data.attending_user_id,
            scheduled_at=data.scheduled_at,
            status=data.status,
            notes=data.notes,
            created_by_id=created_by_id,
        )
        db.add(ap)
        db.commit()
        db.refresh(ap)
        return ap

    @staticmethod
    def update(
        db: Session,
        appt_id: int,
        data: AppointmentUpdate,
        *,
        actor_id: int,
    ) -> Appointment | None:
        ap = db.get(Appointment, appt_id)
        if not ap:
            return None

        actor_roles = AppointmentService._role_set(db, actor_id)
        secretary = bool(actor_roles.intersection(AppointmentService.ROLES_VIEW_ALL))
        is_assigned_doc = ap.attending_user_id == actor_id
        payload = data.model_dump(exclude_unset=True)

        if not secretary:
            if not is_assigned_doc:
                raise PermissionError("Solo el médico asignado puede actualizar esta cita")
            allowed_keys = {"status", "notes"}
            extra = set(payload.keys()) - allowed_keys
            if extra:
                raise PermissionError(
                    f"El médico solo puede cambiar: {', '.join(sorted(allowed_keys))}"
                )

        for k, v in payload.items():
            setattr(ap, k, v)

        ap.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ap)
        return ap

    @staticmethod
    def delete_if_pending(
        db: Session,
        appt_id: int,
        *,
        actor_id: int,
    ) -> bool:
        roles = AppointmentService._role_set(db, actor_id)
        if not roles.intersection(AppointmentService.ROLES_CREATE):
            raise PermissionError("Solo secretaría o admin pueden eliminar citas")

        ap = db.get(Appointment, appt_id)
        if not ap:
            return False
        if ap.status != "pendiente":
            raise ValueError("Solo se pueden eliminar citas en estado pendiente")
        db.delete(ap)
        db.commit()
        return True
