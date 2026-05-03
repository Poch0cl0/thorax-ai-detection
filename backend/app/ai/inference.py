import logging
import random
from typing import Any

from app.ai.model_loader import load_model
from app.ai.preprocessing import preprocess_input
from app.core.config import settings

logger = logging.getLogger(__name__)


def run_inference(
    study_metadata: dict[str, Any],
    raw_bytes: bytes | None = None,
) -> dict[str, Any]:
    """
    Ejecuta inferencia. Si hay modelo cargado, aquí iría el forward pass.
    Por defecto devuelve un resultado simulado determinista por estudio (sin datos clínicos reales).
    """
    model = load_model()
    features = preprocess_input(study_metadata, raw_bytes)

    if model is not None and isinstance(model, dict) and model.get("kind") == "placeholder":
        model = None

    if model is None:
        uid = str(features.get("study_instance_uid") or features.get("id") or "unknown")
        rng = random.Random(uid)
        risk = round(rng.uniform(0.05, 0.45), 4)
        label = "review_recommended" if risk > 0.25 else "low_suspicion"
        return {
            "risk_score": risk,
            "finding_label": label,
            "details": {
                "mode": "stub",
                "model_version": settings.MODEL_VERSION,
                "features": features,
            },
        }

    # Rama para modelo real (placeholder de salida)
    return {
        "risk_score": 0.0,
        "finding_label": "unknown",
        "details": {"mode": "real_not_implemented", "features": features},
    }
