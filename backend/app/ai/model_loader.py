"""
Cargador de modelos scikit-learn para detección de cáncer de tórax.

Carga los modelos de Logistic Regression y Random Forest desde archivos
.joblib exportados desde scikit-learn. Los modelos se cargan de forma
lazy (al primer uso) y se reutilizan como singletons.

Si los archivos .joblib no existen, el sistema opera en modo stub y
todos los módulos transaccionales (login, pacientes, citas, estudios)
funcionan con normalidad.
"""

import logging
from pathlib import Path
from typing import Any

import joblib

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton state
# ---------------------------------------------------------------------------
_lr_model: Any | None = None
_rf_model: Any | None = None
_models_loaded: bool = False


def load_all_models() -> None:
    """
    Carga ambos modelos scikit-learn desde disco.
    Si los archivos no existen, registra un warning y continúa sin error.
    """
    global _lr_model, _rf_model, _models_loaded

    if _models_loaded:
        logger.debug("Modelos ya cargados — omitiendo recarga")
        return

    # --- Logistic Regression ---
    lr_path = Path(settings.LR_MODEL_PATH)
    if lr_path.is_file():
        try:
            _lr_model = joblib.load(lr_path)
            logger.info("Modelo Logistic Regression cargado desde %s", lr_path)
        except Exception:
            logger.exception("Error al cargar modelo LR desde %s", lr_path)
    else:
        logger.warning("Archivo del modelo LR no encontrado: %s", lr_path)

    # --- Random Forest ---
    rf_path = Path(settings.RF_MODEL_PATH)
    if rf_path.is_file():
        try:
            _rf_model = joblib.load(rf_path)
            logger.info("Modelo Random Forest cargado desde %s", rf_path)
        except Exception:
            logger.exception("Error al cargar modelo RF desde %s", rf_path)
    else:
        logger.warning("Archivo del modelo RF no encontrado: %s", rf_path)

    _models_loaded = True
    loaded = []
    if _lr_model is not None:
        loaded.append("logistic_regression")
    if _rf_model is not None:
        loaded.append("random_forest")
    logger.info("Modelos disponibles: %s", loaded or ["ninguno — modo stub activo"])


def get_model(model_type: str) -> Any:
    """
    Retorna el modelo solicitado.

    Args:
        model_type: ``"logistic_regression"`` o ``"random_forest"``

    Raises:
        ValueError: si model_type no es válido o el modelo no está cargado.
    """
    if not _models_loaded:
        load_all_models()

    if model_type == "logistic_regression":
        if _lr_model is None:
            raise ValueError(
                "Modelo de Regresión Logística no está disponible. "
                "Verifica que exista el archivo modelo_lr.joblib."
            )
        return _lr_model
    elif model_type == "random_forest":
        if _rf_model is None:
            raise ValueError(
                "Modelo de Random Forest no está disponible. "
                "Verifica que exista el archivo modelo_rf.joblib."
            )
        return _rf_model
    else:
        raise ValueError(
            f"Tipo de modelo no válido: '{model_type}'. "
            "Opciones: 'logistic_regression', 'random_forest'"
        )


def get_available_models() -> list[str]:
    """Retorna la lista de modelos cargados y disponibles."""
    if not _models_loaded:
        load_all_models()
    available = []
    if _lr_model is not None:
        available.append("logistic_regression")
    if _rf_model is not None:
        available.append("random_forest")
    return available
