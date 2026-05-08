import asyncio
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.ai.inference import run_inference
from app.audit.service import AuditService
from app.core.config import settings
from app.models import Prediction, Study
from app.schemas.prediction import PredictionCreate

logger = logging.getLogger(__name__)


def load_study_image_bytes(study: Study) -> bytes | None:
    key = study.image_storage_key
    if not key or not key.strip():
        return None
    candidate = Path(key)
    abs_path = candidate if candidate.is_file() else (Path(settings.UPLOAD_ROOT) / key)
    try:
        if abs_path.is_file():
            return abs_path.read_bytes()
    except OSError:
        logger.warning("No se pudo leer imagen del estudio %s desde %s", study.id, abs_path)
    return None


class PredictionService:
    @staticmethod
    async def run_and_store(
        db: Session,
        data: PredictionCreate,
        *,
        user_id: int | None,
    ) -> Prediction:
        study = db.query(Study).filter(Study.id == data.study_id).first()
        if not study:
            raise ValueError("Estudio no encontrado")

        meta: dict[str, Any] = {
            "id": study.id,
            "modality": study.modality,
            "study_instance_uid": study.study_instance_uid,
            "patient_id": study.patient_id,
        }

        pixel_bytes = load_study_image_bytes(study)
        timeout = settings.INFERENCE_TIMEOUT_SECONDS

        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(run_inference, meta, pixel_bytes),
                timeout=timeout,
            )
        except asyncio.TimeoutError as exc:
            logger.exception("Inferencia excedió timeout (%ss)", timeout)
            raise TimeoutError(
                f"Inferencia superó el tiempo máximo ({timeout}s)"
            ) from exc

        pred_details = raw.get("details")
        mv = settings.MODEL_VERSION
        if isinstance(pred_details, dict) and "model_version" in pred_details:
            mv = str(pred_details["model_version"])

        prediction = Prediction(
            study_id=study.id,
            created_by_id=user_id,
            model_version=mv,
            risk_score=raw.get("risk_score"),
            finding_label=str(raw.get("finding_label", "unknown")),
            details=pred_details if isinstance(pred_details, dict) else raw.get("details"),
        )
        if isinstance(prediction.details, dict):
            prediction.details.setdefault("model_version", settings.MODEL_VERSION)

        db.add(prediction)
        AuditService.add_entry(
            db,
            action="prediction.created",
            entity_type="prediction",
            entity_id=None,
            user_id=user_id,
            details={
                "study_id": study.id,
                "finding_label": prediction.finding_label,
            },
        )
        db.commit()
        db.refresh(prediction)

        return prediction

    @staticmethod
    def get(db: Session, prediction_id: int) -> Prediction | None:
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    @staticmethod
    def list_for_study(db: Session, study_id: int) -> list[Prediction]:
        return (
            db.query(Prediction)
            .filter(Prediction.study_id == study_id)
            .order_by(Prediction.id.desc())
            .all()
        )
