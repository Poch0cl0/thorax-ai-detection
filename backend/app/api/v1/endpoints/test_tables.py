"""
Endpoints de prueba para las tablas reales de la BD AWS:
  users · patients · appointments · diagnoses
Se usa SQL directo (text()) para respetar el esquema exacto de PostgreSQL.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(prefix="/test", tags=["Test – tablas BD"])


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _row_to_dict(row: Any) -> dict:
    return dict(row._mapping)


def _not_found(entity: str, id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} con id={id} no encontrado.",
    )


# ═══════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


@router.get("/users", summary="Listar todos los usuarios")
def list_users(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT id, username, email, is_active, created_at FROM users ORDER BY id")
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.get("/users/{user_id}", summary="Obtener usuario por ID")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text("SELECT id, username, email, is_active, created_at FROM users WHERE id = :id"),
        {"id": user_id},
    ).fetchone()
    if not row:
        _not_found("Usuario", user_id)
    return _row_to_dict(row)


@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Crear usuario")
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text(
            """
            INSERT INTO users (username, email, hashed_password, is_active)
            VALUES (:username, :email, :hashed_password, :is_active)
            RETURNING id, username, email, is_active, created_at
            """
        ),
        payload.model_dump(),
    ).fetchone()
    db.commit()
    return _row_to_dict(row)


@router.patch("/users/{user_id}", summary="Actualizar usuario")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> dict:
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos a actualizar.")
    set_clause = ", ".join(f"{col} = :{col}" for col in changes)
    changes["id"] = user_id
    row = db.execute(
        text(f"UPDATE users SET {set_clause} WHERE id = :id RETURNING id, username, email, is_active, created_at"),
        changes,
    ).fetchone()
    db.commit()
    if not row:
        _not_found("Usuario", user_id)
    return _row_to_dict(row)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario")
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    result = db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
    db.commit()
    if result.rowcount == 0:
        _not_found("Usuario", user_id)


# ═══════════════════════════════════════════════════════
# PATIENTS
# ═══════════════════════════════════════════════════════

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: date | None = None
    gender: str | None = None
    medical_record_number: str | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    medical_record_number: str | None = None


@router.get("/patients", summary="Listar todos los pacientes")
def list_patients(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT * FROM patients ORDER BY id")
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.get("/patients/{patient_id}", summary="Obtener paciente por ID")
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text("SELECT * FROM patients WHERE id = :id"),
        {"id": patient_id},
    ).fetchone()
    if not row:
        _not_found("Paciente", patient_id)
    return _row_to_dict(row)


@router.post("/patients", status_code=status.HTTP_201_CREATED, summary="Crear paciente")
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text(
            """
            INSERT INTO patients (first_name, last_name, birth_date, gender, medical_record_number)
            VALUES (:first_name, :last_name, :birth_date, :gender, :medical_record_number)
            RETURNING *
            """
        ),
        payload.model_dump(),
    ).fetchone()
    db.commit()
    return _row_to_dict(row)


@router.patch("/patients/{patient_id}", summary="Actualizar paciente")
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)) -> dict:
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos a actualizar.")
    set_clause = ", ".join(f"{col} = :{col}" for col in changes)
    changes["id"] = patient_id
    row = db.execute(
        text(f"UPDATE patients SET {set_clause} WHERE id = :id RETURNING *"),
        changes,
    ).fetchone()
    db.commit()
    if not row:
        _not_found("Paciente", patient_id)
    return _row_to_dict(row)


@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar paciente")
def delete_patient(patient_id: int, db: Session = Depends(get_db)) -> None:
    result = db.execute(text("DELETE FROM patients WHERE id = :id"), {"id": patient_id})
    db.commit()
    if result.rowcount == 0:
        _not_found("Paciente", patient_id)


# ═══════════════════════════════════════════════════════
# APPOINTMENTS
# ═══════════════════════════════════════════════════════

class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: datetime
    reason: str | None = None
    status: str = "pendiente"


class AppointmentUpdate(BaseModel):
    appointment_date: datetime | None = None
    reason: str | None = None
    status: str | None = None


@router.get("/appointments", summary="Listar todas las citas")
def list_appointments(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT * FROM appointments ORDER BY id")
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.get("/appointments/{appointment_id}", summary="Obtener cita por ID")
def get_appointment(appointment_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text("SELECT * FROM appointments WHERE id = :id"),
        {"id": appointment_id},
    ).fetchone()
    if not row:
        _not_found("Cita", appointment_id)
    return _row_to_dict(row)


@router.get("/appointments/patient/{patient_id}", summary="Citas de un paciente")
def list_appointments_by_patient(patient_id: int, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT * FROM appointments WHERE patient_id = :pid ORDER BY appointment_date"),
        {"pid": patient_id},
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.post("/appointments", status_code=status.HTTP_201_CREATED, summary="Crear cita")
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text(
            """
            INSERT INTO appointments (patient_id, appointment_date, reason, status)
            VALUES (:patient_id, :appointment_date, :reason, :status)
            RETURNING *
            """
        ),
        payload.model_dump(),
    ).fetchone()
    db.commit()
    return _row_to_dict(row)


@router.patch("/appointments/{appointment_id}", summary="Actualizar cita")
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)) -> dict:
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos a actualizar.")
    set_clause = ", ".join(f"{col} = :{col}" for col in changes)
    changes["id"] = appointment_id
    row = db.execute(
        text(f"UPDATE appointments SET {set_clause} WHERE id = :id RETURNING *"),
        changes,
    ).fetchone()
    db.commit()
    if not row:
        _not_found("Cita", appointment_id)
    return _row_to_dict(row)


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar cita")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)) -> None:
    result = db.execute(text("DELETE FROM appointments WHERE id = :id"), {"id": appointment_id})
    db.commit()
    if result.rowcount == 0:
        _not_found("Cita", appointment_id)


# ═══════════════════════════════════════════════════════
# DIAGNOSES
# ═══════════════════════════════════════════════════════

class DiagnosisCreate(BaseModel):
    patient_id: int
    image_url: str | None = None
    prediction_label: str | None = None
    lr_probability: float | None = None
    rf_probability: float | None = None


class DiagnosisUpdate(BaseModel):
    image_url: str | None = None
    prediction_label: str | None = None
    lr_probability: float | None = None
    rf_probability: float | None = None


@router.get("/diagnoses", summary="Listar todos los diagnósticos")
def list_diagnoses(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT * FROM diagnoses ORDER BY id")
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.get("/diagnoses/{diagnosis_id}", summary="Obtener diagnóstico por ID")
def get_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text("SELECT * FROM diagnoses WHERE id = :id"),
        {"id": diagnosis_id},
    ).fetchone()
    if not row:
        _not_found("Diagnóstico", diagnosis_id)
    return _row_to_dict(row)


@router.get("/diagnoses/patient/{patient_id}", summary="Diagnósticos de un paciente")
def list_diagnoses_by_patient(patient_id: int, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        text("SELECT * FROM diagnoses WHERE patient_id = :pid ORDER BY created_at DESC"),
        {"pid": patient_id},
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


@router.post("/diagnoses", status_code=status.HTTP_201_CREATED, summary="Crear diagnóstico")
def create_diagnosis(payload: DiagnosisCreate, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        text(
            """
            INSERT INTO diagnoses (patient_id, image_url, prediction_label, lr_probability, rf_probability)
            VALUES (:patient_id, :image_url, :prediction_label, :lr_probability, :rf_probability)
            RETURNING *
            """
        ),
        payload.model_dump(),
    ).fetchone()
    db.commit()
    return _row_to_dict(row)


@router.patch("/diagnoses/{diagnosis_id}", summary="Actualizar diagnóstico")
def update_diagnosis(diagnosis_id: int, payload: DiagnosisUpdate, db: Session = Depends(get_db)) -> dict:
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=400, detail="No se enviaron campos a actualizar.")
    set_clause = ", ".join(f"{col} = :{col}" for col in changes)
    changes["id"] = diagnosis_id
    row = db.execute(
        text(f"UPDATE diagnoses SET {set_clause} WHERE id = :id RETURNING *"),
        changes,
    ).fetchone()
    db.commit()
    if not row:
        _not_found("Diagnóstico", diagnosis_id)
    return _row_to_dict(row)


@router.delete("/diagnoses/{diagnosis_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar diagnóstico")
def delete_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)) -> None:
    result = db.execute(text("DELETE FROM diagnoses WHERE id = :id"), {"id": diagnosis_id})
    db.commit()
    if result.rowcount == 0:
        _not_found("Diagnóstico", diagnosis_id)
