from typing import Any


def preprocess_input(
    study_metadata: dict[str, Any],
    raw_bytes: bytes | None,
) -> dict[str, Any]:
    """
    Normaliza metadatos del estudio y, si aplica, prepara tensores/imagen.
    Sin imagen real, solo propaga metadatos para la ruta simulada.
    """
    return {
        "modality": study_metadata.get("modality", "CT"),
        "study_instance_uid": study_metadata.get("study_instance_uid"),
        "has_pixel_data": raw_bytes is not None and len(raw_bytes) > 0,
    }
