"""
Motor de inferencia para detección de cáncer de tórax.

Utiliza los modelos PySpark ML (Logistic Regression y Random Forest)
para clasificar imágenes de radiografía como "cancer" o "normal".
"""

import logging
import random
from typing import Any

from app.ai.model_loader import get_model, get_spark
from app.ai.preprocessing import preprocess_image, preprocess_input
from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeo de niveles de riesgo
# ---------------------------------------------------------------------------
_RISK_LEVELS = {
    "alto": {"min": 0.65, "label": "Alto", "color": "red"},
    "moderado": {"min": 0.35, "label": "Moderado", "color": "yellow"},
    "bajo": {"min": 0.0, "label": "Bajo", "color": "green"},
}


def _classify_risk(prob_cancer: float) -> str:
    """Clasifica el nivel de riesgo según la probabilidad de cáncer."""
    if prob_cancer >= 0.65:
        return "alto"
    elif prob_cancer >= 0.35:
        return "moderado"
    return "bajo"


def _generate_recommendation(prediction_label: str, risk_level: str) -> str:
    """Genera una recomendación textual basada en la predicción."""
    if prediction_label == "cancer_detected":
        if risk_level == "alto":
            return (
                "Se ha detectado una alta probabilidad de presencia de "
                "anomalías compatibles con cáncer. Se recomienda de forma "
                "urgente consultar con un especialista en oncología torácica "
                "y realizar estudios complementarios (biopsia, PET-CT)."
            )
        return (
            "Se han detectado posibles anomalías. Se recomienda consultar "
            "con un especialista y realizar estudios adicionales para "
            "confirmar o descartar el diagnóstico."
        )
    else:
        if risk_level == "bajo":
            return (
                "No se detectaron anomalías significativas en la imagen. "
                "Se recomienda continuar con los controles de rutina según "
                "la indicación de su médico."
            )
        return (
            "Aunque no se detectaron anomalías principales, el nivel de "
            "confianza es moderado. Se sugiere una evaluación clínica "
            "complementaria."
        )


_DISCLAIMER = (
    "⚠️ AVISO: Este sistema es una herramienta de apoyo académico y NO "
    "sustituye el diagnóstico médico profesional. Los resultados deben ser "
    "interpretados exclusivamente por personal de salud calificado. "
    "No tome decisiones médicas basándose únicamente en esta predicción."
)


def run_scan_inference(
    image_bytes: bytes,
    model_type: str = "random_forest",
) -> dict[str, Any]:
    """
    Ejecuta la inferencia completa sobre una imagen de radiografía.

    Args:
        image_bytes: Bytes crudos de la imagen (JPEG, PNG, etc.)
        model_type: ``"logistic_regression"`` o ``"random_forest"``

    Returns:
        Diccionario con predicción, probabilidades, nivel de riesgo,
        recomendación y disclaimer.

    Raises:
        ValueError: si el modelo o la imagen no son válidos.
        RuntimeError: si ocurre un error durante la inferencia.
    """
    # 1. Preprocesar imagen → vector de 4096 features
    features_array = preprocess_image(image_bytes)

    # 2. Obtener modelo y Spark session
    model = get_model(model_type)
    spark = get_spark()

    try:
        from pyspark.ml.linalg import Vectors

        # 3. Crear DataFrame de Spark con una fila
        dense_vector = Vectors.dense(features_array.tolist())
        df = spark.createDataFrame([(dense_vector,)], ["features"])

        # 4. Ejecutar transformación del modelo
        result_df = model.transform(df)

        # 5. Extraer resultados
        row = result_df.select(
            "prediction", "probability"
        ).first()

        prediction_value = float(row["prediction"])  # 0.0 o 1.0
        probability_vector = row["probability"]      # DenseVector[prob_0, prob_1]

        prob_normal = float(probability_vector[0])
        prob_cancer = float(probability_vector[1])

    except Exception as exc:
        logger.exception("Error durante la inferencia PySpark")
        raise RuntimeError(
            "Error al ejecutar la predicción del modelo. "
            "Intente nuevamente o use otro modelo."
        ) from exc

    # 6. Determinar etiqueta y nivel de riesgo
    prediction_label = (
        "cancer_detected" if prediction_value == 1.0 else "no_cancer"
    )
    risk_level = _classify_risk(prob_cancer)
    confidence = max(prob_cancer, prob_normal) * 100

    # 7. Construir respuesta
    model_display_names = {
        "logistic_regression": "Regresión Logística",
        "random_forest": "Random Forest",
    }

    return {
        "prediction": prediction_label,
        "probability_cancer": round(prob_cancer, 6),
        "probability_normal": round(prob_normal, 6),
        "risk_level": risk_level,
        "model_used": model_type,
        "model_display_name": model_display_names.get(model_type, model_type),
        "model_version": settings.MODEL_VERSION,
        "confidence_percent": round(confidence, 2),
        "recommendation": _generate_recommendation(prediction_label, risk_level),
        "disclaimer": _DISCLAIMER,
    }


def run_inference(
    study_metadata: dict[str, Any],
    raw_bytes: bytes | None = None,
) -> dict[str, Any]:
    """
    Ejecuta inferencia — compatible con el flujo existente de estudios.

    Si hay imagen (raw_bytes) y los modelos están disponibles, usa
    inferencia real. Si no, recurre a la inferencia simulada.
    """
    from app.ai.model_loader import get_available_models

    available = get_available_models()

    # Si hay imagen y modelos disponibles, usar inferencia real
    if raw_bytes and available:
        try:
            model_type = available[0]  # Usar el primer modelo disponible
            return run_scan_inference(raw_bytes, model_type)
        except Exception:
            logger.warning(
                "Inferencia real falló, recurriendo a modo simulado"
            )

    # Inferencia simulada (compatibilidad)
    features = preprocess_input(study_metadata, raw_bytes)
    uid = str(
        features.get("study_instance_uid")
        or features.get("id")
        or "unknown"
    )
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
