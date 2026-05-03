import logging
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

_loaded_artifact: Any | None = None


def load_model() -> Any | None:
    """
    Carga el artefacto del modelo desde MODEL_PATH.
    Si no hay ruta o archivo, devuelve None (inferencia simulada).
    """
    global _loaded_artifact
    if _loaded_artifact is not None:
        return _loaded_artifact

    path = settings.MODEL_PATH
    if not path:
        logger.info("MODEL_PATH no configurado; se usará inferencia simulada")
        return None

    p = Path(path)
    if not p.is_file():
        logger.warning("MODEL_PATH no es un archivo válido: %s", path)
        return None

    # Aquí: torch.load, onnxruntime.InferenceSession, etc.
    logger.warning(
        "Carga real no implementada; coloca aquí la carga para %s",
        path,
    )
    _loaded_artifact = {"path": str(p.resolve()), "kind": "placeholder"}
    return _loaded_artifact


def clear_model_cache() -> None:
    global _loaded_artifact
    _loaded_artifact = None
