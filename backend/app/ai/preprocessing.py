"""
Preprocesamiento de imágenes de radiografía de tórax.

Pipeline: imagen → escala de grises → resize 64×64 → normalizar [0,1] → flatten → 4096 features
Compatible con el entrenamiento realizado en Google Colab con PySpark ML.
"""
from __future__ import annotations

import io
import logging

import numpy as np
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

# Formatos de imagen aceptados
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/tiff",
    "image/webp",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def validate_image_bytes(raw_bytes: bytes, content_type: str | None = None) -> None:
    """
    Valida que los bytes correspondan a una imagen válida y dentro del
    tamaño permitido.

    Raises:
        ValueError: si la imagen no es válida, está corrupta o excede el tamaño.
    """
    if not raw_bytes:
        raise ValueError("No se recibieron datos de imagen")

    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(raw_bytes) > max_bytes:
        raise ValueError(
            f"La imagen excede el tamaño máximo permitido "
            f"({settings.MAX_IMAGE_SIZE_MB} MB)"
        )

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Tipo de archivo no soportado: '{content_type}'. "
            f"Formatos aceptados: JPEG, PNG, BMP, TIFF, WebP"
        )

    # Intentar abrir para verificar que no esté corrupta
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()
    except Exception as exc:
        raise ValueError(
            "El archivo no es una imagen válida o está corrupto"
        ) from exc


def preprocess_image(raw_bytes: bytes) -> np.ndarray:
    """
    Preprocesa una imagen de radiografía de tórax para inferencia.

    Pipeline:
        1. Abrir imagen con Pillow
        2. Convertir a escala de grises (mode "L")
        3. Redimensionar a IMAGE_SIZE × IMAGE_SIZE (64×64 por defecto)
        4. Normalizar valores de píxel a [0.0, 1.0]
        5. Aplanar a vector 1D de IMAGE_SIZE² elementos (4096)

    Args:
        raw_bytes: Bytes de la imagen (JPEG, PNG, etc.)

    Returns:
        Array numpy float64 de forma ``(IMAGE_SIZE**2,)`` con valores en [0, 1].

    Raises:
        ValueError: si la imagen no puede procesarse.
    """
    size = settings.IMAGE_SIZE  # 64

    try:
        img = Image.open(io.BytesIO(raw_bytes))

        # Convertir a escala de grises
        if img.mode != "L":
            img = img.convert("L")

        # Redimensionar con anti-alias
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Convertir a array numpy y normalizar
        pixel_array = np.array(img, dtype=np.float64) / 255.0

        # Aplanar a vector 1D
        features = pixel_array.flatten()

        logger.debug(
            "Imagen preprocesada: shape=%s, min=%.4f, max=%.4f",
            features.shape, features.min(), features.max(),
        )

        if features.shape[0] != size * size:
            raise ValueError(
                f"Vector de features tiene tamaño inesperado: "
                f"{features.shape[0]} (esperado {size * size})"
            )

        return features

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "Error al preprocesar la imagen. Verifica que sea un "
            "archivo de imagen válido (JPEG, PNG, BMP, TIFF)."
        ) from exc


def preprocess_input(
    study_metadata: dict, raw_bytes: bytes | None = None,
) -> dict:
    """
    Normaliza metadatos del estudio y, si aplica, extrae información básica
    desde píxeles (RX/PNG/JPEG típicos demo).
    """
    from typing import Any

    out: dict[str, Any] = {
        "modality": study_metadata.get("modality", "CT"),
        "study_instance_uid": study_metadata.get("study_instance_uid"),
        "has_pixel_data": raw_bytes is not None and len(raw_bytes) > 0,
    }
    if not out["has_pixel_data"] or raw_bytes is None:
        return out

    try:
        from PIL import Image  # type: ignore[import-untyped]

        with Image.open(io.BytesIO(raw_bytes)) as img:
            im = img.convert("L")
            w, h = im.size
            out["pil_width"], out["pil_height"] = w, h
            arr = []
            px = list(im.resize((96, 96)).getdata())
            if px:
                out["pil_mean_gray"] = sum(px) / len(px)
    except ImportError:
        out["pil_unavailable"] = True
    except Exception as exc:
        out["pil_error"] = str(exc)

    if raw_bytes:
        try:
            features = preprocess_image(raw_bytes)
            out["features"] = features.tolist()
        except ValueError:
            logger.warning("No se pudo preprocesar la imagen del estudio")

    return out
