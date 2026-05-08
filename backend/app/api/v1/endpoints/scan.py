"""
Endpoint para análisis de imágenes de radiografía de tórax.

Permite subir una imagen y obtener una predicción de cáncer sin
necesidad de autenticación (diseñado para demo / uso público).
"""

import asyncio
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.ai.inference import run_scan_inference
from app.ai.model_loader import get_available_models
from app.ai.preprocessing import ALLOWED_MIME_TYPES, validate_image_bytes
from app.core.config import settings
from app.schemas.scan import ModelsInfoResponse, ScanAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan", tags=["scan"])

# Nombres legibles para la UI
_MODEL_LABELS = {
    "logistic_regression": "Regresión Logística",
    "random_forest": "Random Forest",
}


@router.post(
    "/analyze",
    response_model=ScanAnalysisResponse,
    summary="Analizar radiografía de tórax",
    description=(
        "Sube una imagen de radiografía transversal de tórax y recibe "
        "una predicción de cáncer con probabilidades y nivel de riesgo. "
        "Formatos aceptados: JPEG, PNG, BMP, TIFF, WebP."
    ),
)
async def analyze_scan(
    file: UploadFile = File(
        ...,
        description="Imagen de radiografía de tórax (JPEG, PNG, BMP, TIFF, WebP)",
    ),
    model_type: str = Form(
        default="random_forest",
        description="Tipo de modelo: 'logistic_regression' o 'random_forest'",
    ),
) -> ScanAnalysisResponse:
    """Analiza una imagen de radiografía de tórax para detección de cáncer."""

    # 1. Validar que hay modelos disponibles
    available = get_available_models()
    if not available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No hay modelos de IA disponibles. "
                "Contacte al administrador del sistema."
            ),
        )

    # 2. Validar tipo de modelo
    if model_type not in ("logistic_regression", "random_forest"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Tipo de modelo no válido: '{model_type}'. "
                "Opciones: 'logistic_regression', 'random_forest'"
            ),
        )

    if model_type not in available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"El modelo '{model_type}' no está disponible actualmente. "
                f"Modelos disponibles: {available}"
            ),
        )

    # 3. Leer y validar la imagen
    try:
        raw_bytes = await file.read()
    except Exception as exc:
        logger.exception("Error al leer el archivo subido")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al leer el archivo subido",
        ) from exc

    try:
        validate_image_bytes(raw_bytes, file.content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # 4. Ejecutar inferencia en un thread separado (es bloqueante por Spark)
    timeout = settings.INFERENCE_TIMEOUT_SECONDS

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(run_scan_inference, raw_bytes, model_type),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        logger.error("Inferencia excedió timeout de %ss", timeout)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                f"El análisis excedió el tiempo máximo ({timeout}s). "
                "Intente nuevamente o use otro modelo."
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    logger.info(
        "Scan analizado: modelo=%s, predicción=%s, prob_cancer=%.4f",
        model_type,
        result["prediction"],
        result["probability_cancer"],
    )

    return ScanAnalysisResponse(**result)


@router.get(
    "/models",
    response_model=ModelsInfoResponse,
    summary="Listar modelos disponibles",
    description="Retorna la lista de modelos de IA cargados y disponibles.",
)
async def list_models() -> ModelsInfoResponse:
    """Retorna los modelos disponibles para análisis."""
    available = get_available_models()

    model_options = [
        {
            "value": m,
            "label": _MODEL_LABELS.get(m, m),
            "description": (
                "Modelo lineal rápido con buena interpretabilidad"
                if m == "logistic_regression"
                else "Modelo ensemble con alta precisión"
            ),
        }
        for m in available
    ]

    return ModelsInfoResponse(
        available_models=available,
        model_options=model_options,
    )
