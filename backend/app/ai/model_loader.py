"""
Cargador de modelos PySpark ML para detección de cáncer de tórax.

Inicializa una SparkSession en modo local y carga los modelos de
Logistic Regression y Random Forest entrenados previamente en Colab.
Los modelos se cargan una sola vez (singleton) y se reutilizan.
"""

import logging
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton state
# ---------------------------------------------------------------------------
_spark_session: Any | None = None
_lr_model: Any | None = None
_rf_model: Any | None = None
_models_loaded: bool = False


def _get_or_create_spark() -> Any:
    """Crea o reutiliza la SparkSession en modo local."""
    global _spark_session
    if _spark_session is not None:
        return _spark_session

    try:
        from pyspark.sql import SparkSession

        _spark_session = (
            SparkSession.builder
            .master("local[*]")
            .appName("ThoraxAI-Inference")
            .config("spark.driver.memory", "1g")
            .config("spark.ui.enabled", "false")          # No UI para servidor web
            .config("spark.sql.shuffle.partitions", "2")   # Mínimo para single-row
            .config("spark.driver.host", "localhost")
            .getOrCreate()
        )
        # Reducir verbosidad de logs de Spark
        _spark_session.sparkContext.setLogLevel("ERROR")
        logger.info("SparkSession inicializada en modo local")
    except Exception:
        logger.exception("Error al inicializar SparkSession")
        raise

    return _spark_session


def load_all_models() -> None:
    """
    Carga ambos modelos PySpark ML desde disco.
    Diseñado para ejecutarse una vez al iniciar el servidor.
    """
    global _lr_model, _rf_model, _models_loaded

    if _models_loaded:
        logger.debug("Modelos ya cargados — omitiendo recarga")
        return

    spark = _get_or_create_spark()  # noqa: F841 — asegura que la sesión existe

    # --- Logistic Regression ---
    lr_path = Path(settings.LR_MODEL_PATH)
    if lr_path.is_dir():
        try:
            from pyspark.ml.classification import LogisticRegressionModel

            _lr_model = LogisticRegressionModel.load(str(lr_path.resolve()))
            logger.info(
                "Modelo Logistic Regression cargado desde %s", lr_path
            )
        except Exception:
            logger.exception("Error al cargar modelo LR desde %s", lr_path)
    else:
        logger.warning(
            "Directorio del modelo LR no encontrado: %s", lr_path
        )

    # --- Random Forest ---
    rf_path = Path(settings.RF_MODEL_PATH)
    if rf_path.is_dir():
        try:
            from pyspark.ml.classification import (
                RandomForestClassificationModel,
            )

            _rf_model = RandomForestClassificationModel.load(
                str(rf_path.resolve())
            )
            logger.info(
                "Modelo Random Forest cargado desde %s", rf_path
            )
        except Exception:
            logger.exception("Error al cargar modelo RF desde %s", rf_path)
    else:
        logger.warning(
            "Directorio del modelo RF no encontrado: %s", rf_path
        )

    _models_loaded = True
    loaded = []
    if _lr_model is not None:
        loaded.append("logistic_regression")
    if _rf_model is not None:
        loaded.append("random_forest")
    logger.info("Modelos disponibles: %s", loaded or ["ninguno"])


def get_spark() -> Any:
    """Retorna la SparkSession activa."""
    if _spark_session is None:
        return _get_or_create_spark()
    return _spark_session


def get_model(model_type: str) -> Any:
    """
    Retorna el modelo solicitado.

    Args:
        model_type: ``"logistic_regression"`` o ``"random_forest"``

    Raises:
        ValueError: si *model_type* no es válido o el modelo no está cargado.
    """
    if not _models_loaded:
        load_all_models()

    if model_type == "logistic_regression":
        if _lr_model is None:
            raise ValueError(
                "Modelo de Regresión Logística no está disponible. "
                "Verifica que exista el directorio del modelo."
            )
        return _lr_model
    elif model_type == "random_forest":
        if _rf_model is None:
            raise ValueError(
                "Modelo de Random Forest no está disponible. "
                "Verifica que exista el directorio del modelo."
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


def shutdown_spark() -> None:
    """Cierra la SparkSession de forma ordenada."""
    global _spark_session, _lr_model, _rf_model, _models_loaded
    if _spark_session is not None:
        try:
            _spark_session.stop()
            logger.info("SparkSession detenida")
        except Exception:
            logger.exception("Error al detener SparkSession")
    _spark_session = None
    _lr_model = None
    _rf_model = None
    _models_loaded = False
