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
    Ejecuta inferencia asistida. Si hay modelo real configurado devuelve
    salida provisional; si no, resultados simulados acotados a apoyo clínico
    (no diagnóstico definitivo).
    """
    model = load_model()
    features = preprocess_input(study_metadata, raw_bytes)

    if model is not None and isinstance(model, dict) and model.get("kind") == "placeholder":
        model = None

    if model is None:
        uid = str(features.get("study_instance_uid") or features.get("id") or "unknown")
        rng = random.Random(uid)
        base_scale = rng.uniform(0.05, 0.95)
        if features.get("has_pixel_data"):
            mean_g = features.get("pil_mean_gray")
            jitter = rng.uniform(-0.12, 0.12)
            if isinstance(mean_g, (int, float)):
                risk_raw = (
                    abs(float(mean_g) - 127.5) / 127.5 * (0.4 + jitter) + 0.05
                )
            else:
                risk_raw = base_scale + jitter
            risk = round(min(0.99, max(0.05, risk_raw)), 4)
            label_es = (
                "requiere_revision_especializada"
                if risk > 0.45
                else "baja_sospecha_apoyo_ia"
            )
        else:
            risk = round(rng.uniform(0.05, 0.45), 4)
            label_es = (
                "se_recomienda_revision"
                if risk > 0.25
                else "baja_sospecha_apoyo_artificial"
            )
        detail_es = (
            "Resultado de apoyo; no equivale a diagnóstico de cáncer "
            "de tórax por sí solo. Valide con criterio clínico."
        )
        return {
            "risk_score": risk,
            "finding_label": label_es,
            "details": {
                "mode": "stub_visual" if features.get("has_pixel_data") else "stub_metadata_only",
                "model_version": settings.MODEL_VERSION,
                "clinical_disclaimer_es": detail_es,
                "features": features,
            },
        }

    logger.warning(
        "Modelo real placeholder; completar inferencia ONNX/Torch usando features"
    )
    return {
        "risk_score": 0.1,
        "finding_label": "analisis_modelo_placeholder",
        "details": {
            "mode": "real_not_implemented",
            "model_version": settings.MODEL_VERSION,
            "features": features,
            "clinical_disclaimer_es": "Complete la rama ML con su artefacto empaquetado.",
        },
    }
