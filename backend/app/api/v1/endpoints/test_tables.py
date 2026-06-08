"""
Endpoints de prueba para las tablas reales de la BD AWS:
  users · patients · appointments · diagnoses
Se usa SQL directo (text()) para respetar el esquema exacto de PostgreSQL.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai.inference import run_scan_inference
from app.ai.model_loader import get_available_models
from app.ai.preprocessing import validate_image_bytes
from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

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


# ═══════════════════════════════════════════════════════
# SCAN + GUARDAR EN DIAGNOSES
# ═══════════════════════════════════════════════════════

@router.post(
    "/diagnose",
    status_code=status.HTTP_201_CREATED,
    summary="Analizar imagen y guardar diagnóstico",
    description=(
        "Sube una radiografía de tórax (JPEG, PNG, BMP, TIFF, WebP), "
        "corre ambos modelos (Regresión Logística y Random Forest), "
        "guarda el resultado en la tabla `diagnoses` y lo retorna."
    ),
    tags=["Test – tablas BD"],
)
async def diagnose_and_save(
    patient_id: int = Form(..., description="ID del paciente en la tabla patients"),
    image_url: str | None = Form(
        default=None,
        description="URL pública de la imagen (opcional, para referencia)",
    ),
    file: UploadFile = File(
        ...,
        description="Imagen de radiografía (JPEG, PNG, BMP, TIFF, WebP — máx 10 MB)",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    1. Valida la imagen.
    2. Corre ambos modelos (LR + RF) en paralelo.
    3. Guarda el resultado en la tabla `diagnoses`.
    4. Retorna el diagnóstico completo.
    """
    # ── 1. Verificar que el paciente existe ─────────────────────────────────
    patient = db.execute(
        text("SELECT id FROM patients WHERE id = :id"), {"id": patient_id}
    ).fetchone()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id={patient_id} no encontrado.",
        )

    # ── 2. Verificar modelos disponibles ────────────────────────────────────
    available = get_available_models()
    if not available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay modelos de IA cargados. Contacte al administrador.",
        )

    # ── 3. Leer y validar la imagen ─────────────────────────────────────────
    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al leer el archivo.",
        ) from exc

    try:
        validate_image_bytes(raw_bytes, file.content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # ── 4. Correr ambos modelos (LR + RF) ───────────────────────────────────
    timeout = settings.INFERENCE_TIMEOUT_SECONDS
    lr_prob: float | None = None
    rf_prob: float | None = None
    lr_label: str | None = None
    rf_label: str | None = None

    async def _run(model_type: str) -> dict:
        return await asyncio.wait_for(
            asyncio.to_thread(run_scan_inference, raw_bytes, model_type),
            timeout=timeout,
        )

    # Ejecutar en paralelo si ambos modelos están disponibles
    tasks: dict[str, asyncio.Task] = {}
    if "logistic_regression" in available:
        tasks["lr"] = asyncio.create_task(_run("logistic_regression"))
    if "random_forest" in available:
        tasks["rf"] = asyncio.create_task(_run("random_forest"))

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ningún modelo compatible está disponible.",
        )

    try:
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"La inferencia superó el tiempo máximo ({timeout}s).",
        )

    result_map: dict[str, dict] = {}
    for key, res in zip(tasks.keys(), results):
        if isinstance(res, Exception):
            logger.warning("Modelo '%s' falló durante inferencia: %s", key, res)
        else:
            result_map[key] = res

    if not result_map:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Todos los modelos fallaron durante la inferencia.",
        )

    if "lr" in result_map:
        lr_prob = result_map["lr"]["probability_cancer"]
        lr_label = result_map["lr"]["prediction"]
    if "rf" in result_map:
        rf_prob = result_map["rf"]["probability_cancer"]
        rf_label = result_map["rf"]["prediction"]

    # Etiqueta final: usa RF si está disponible, si no LR
    primary = result_map.get("rf") or result_map.get("lr")
    prediction_label = primary["prediction"]
    risk_level = primary["risk_level"]
    confidence_percent = primary["confidence_percent"]
    recommendation = primary["recommendation"]

    # ── 5. Guardar en tabla diagnoses ────────────────────────────────────────
    row = db.execute(
        text(
            """
            INSERT INTO diagnoses (patient_id, image_url, prediction_label, lr_probability, rf_probability)
            VALUES (:patient_id, :image_url, :prediction_label, :lr_probability, :rf_probability)
            RETURNING *
            """
        ),
        {
            "patient_id": patient_id,
            "image_url": image_url,
            "prediction_label": prediction_label,
            "lr_probability": lr_prob,
            "rf_probability": rf_prob,
        },
    ).fetchone()
    db.commit()

    saved = _row_to_dict(row)

    # ── 6. Respuesta enriquecida ─────────────────────────────────────────────
    return {
        **saved,
        "risk_level": risk_level,
        "confidence_percent": confidence_percent,
        "recommendation": recommendation,
        "disclaimer": (
            "AVISO: Este sistema es una herramienta de apoyo académico y NO "
            "sustituye el diagnóstico médico profesional."
        ),
        "models_used": list(result_map.keys()),
    }


# ═══════════════════════════════════════════════════════
# DYNAMO DB — DIAGNÓSTICOS
# ═══════════════════════════════════════════════════════

@router.post(
    "/diagnose-dual",
    status_code=status.HTTP_201_CREATED,
    summary="Analizar imagen → guardar en RDS + DynamoDB",
    description=(
        "Corre ambos modelos de IA sobre la radiografía, guarda el resultado "
        "en la tabla `diagnoses` de PostgreSQL (RDS) **y** replica el documento "
        "en DynamoDB (`thorax_diagnoses`). "
        "Retorna el diagnóstico completo con confirmación de ambas escrituras."
    ),
)
async def diagnose_dual(
    patient_id: int = Form(..., description="ID del paciente en la tabla patients"),
    image_url: str | None = Form(default=None, description="URL pública de la imagen (opcional)"),
    file: UploadFile = File(..., description="Radiografía de tórax (JPEG, PNG, BMP, TIFF, WebP)"),
    db: Session = Depends(get_db),
) -> dict:
    """Análisis completo con escritura dual RDS + DynamoDB."""
    from app.services.dynamo_service import save_diagnosis

    # ── 1. Verificar paciente ────────────────────────────────────────────────
    patient = db.execute(
        text("SELECT id FROM patients WHERE id = :id"), {"id": patient_id}
    ).fetchone()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Paciente id={patient_id} no encontrado.")

    # ── 2. Verificar modelos ─────────────────────────────────────────────────
    available = get_available_models()
    if not available:
        raise HTTPException(status_code=503, detail="No hay modelos de IA cargados.")

    # ── 3. Validar imagen ────────────────────────────────────────────────────
    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Error al leer el archivo.") from exc

    try:
        validate_image_bytes(raw_bytes, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # ── 4. Inferencia ambos modelos ──────────────────────────────────────────
    timeout = settings.INFERENCE_TIMEOUT_SECONDS
    lr_prob: float | None = None
    rf_prob: float | None = None

    async def _run(model_type: str) -> dict:
        return await asyncio.wait_for(
            asyncio.to_thread(run_scan_inference, raw_bytes, model_type),
            timeout=timeout,
        )

    tasks: dict[str, asyncio.Task] = {}
    if "logistic_regression" in available:
        tasks["lr"] = asyncio.create_task(_run("logistic_regression"))
    if "random_forest" in available:
        tasks["rf"] = asyncio.create_task(_run("random_forest"))

    raw_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    result_map: dict[str, dict] = {}
    for key, res in zip(tasks.keys(), raw_results):
        if not isinstance(res, Exception):
            result_map[key] = res

    if not result_map:
        raise HTTPException(status_code=500, detail="Todos los modelos fallaron.")

    if "lr" in result_map:
        lr_prob = result_map["lr"]["probability_cancer"]
    if "rf" in result_map:
        rf_prob = result_map["rf"]["probability_cancer"]

    primary = result_map.get("rf") or result_map.get("lr")
    prediction_label = primary["prediction"]
    risk_level = primary["risk_level"]
    confidence_percent = primary["confidence_percent"]
    recommendation = primary["recommendation"]

    # ── 5. Guardar en RDS (PostgreSQL) ───────────────────────────────────────
    row = db.execute(
        text(
            """
            INSERT INTO diagnoses (patient_id, image_url, prediction_label, lr_probability, rf_probability)
            VALUES (:patient_id, :image_url, :prediction_label, :lr_probability, :rf_probability)
            RETURNING *
            """
        ),
        {
            "patient_id": patient_id,
            "image_url": image_url,
            "prediction_label": prediction_label,
            "lr_probability": lr_prob,
            "rf_probability": rf_prob,
        },
    ).fetchone()
    db.commit()
    saved = _row_to_dict(row)

    enriched = {
        **saved,
        "risk_level": risk_level,
        "confidence_percent": confidence_percent,
        "recommendation": recommendation,
    }

    # ── 6. Guardar en DynamoDB ───────────────────────────────────────────────
    dynamo_ok = False
    dynamo_error: str | None = None
    dynamo_indexed_at: str | None = None

    try:
        result_with_dynamo = save_diagnosis(enriched)
        dynamo_indexed_at = result_with_dynamo.get("dynamo_indexed_at")
        dynamo_ok = True
    except (ValueError, RuntimeError) as exc:
        dynamo_error = str(exc)
        logger.warning("DynamoDB write failed: %s", exc)

    return {
        **enriched,
        "disclaimer": (
            "AVISO: Este sistema es una herramienta de apoyo académico y NO "
            "sustituye el diagnóstico médico profesional."
        ),
        "models_used": list(result_map.keys()),
        "storage": {
            "rds": {"ok": True, "table": "diagnoses"},
            "dynamodb": {
                "ok": dynamo_ok,
                "table": settings.DYNAMO_TABLE_NAME,
                "indexed_at": dynamo_indexed_at,
                "error": dynamo_error,
            },
        },
    }


@router.get(
    "/dynamo/diagnoses/{diagnosis_id}",
    summary="Leer diagnóstico desde DynamoDB",
    description="Obtiene un diagnóstico directamente de DynamoDB por su ID.",
)
def get_diagnosis_dynamo(diagnosis_id: int) -> dict:
    from app.services.dynamo_service import get_diagnosis_from_dynamo
    try:
        item = get_diagnosis_from_dynamo(diagnosis_id)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    if not item:
        raise HTTPException(status_code=404, detail=f"Diagnóstico id={diagnosis_id} no encontrado en DynamoDB.")
    return item


@router.get(
    "/dynamo/diagnoses/patient/{patient_id}",
    summary="Listar diagnósticos de un paciente desde DynamoDB",
    description="Escanea DynamoDB y retorna todos los diagnósticos del paciente.",
)
def list_diagnoses_patient_dynamo(patient_id: int) -> list[dict]:
    from app.services.dynamo_service import list_diagnoses_by_patient_dynamo
    try:
        return list_diagnoses_by_patient_dynamo(patient_id)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post(
    "/dynamo/ensure-table",
    summary="Crear tabla DynamoDB si no existe",
    description=(
        "Verifica si la tabla `thorax_diagnoses` existe en DynamoDB. "
        "Si no existe, la crea automáticamente con billing PAY_PER_REQUEST."
    ),
)
def ensure_dynamo_table() -> dict:
    from app.services.dynamo_service import ensure_table_exists
    try:
        already_existed = ensure_table_exists()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {
        "table": settings.DYNAMO_TABLE_NAME,
        "region": settings.AWS_REGION,
        "already_existed": already_existed,
        "status": "ok",
    }
