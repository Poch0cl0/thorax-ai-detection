"""
Conversión de modelos PySpark ML (formato Parquet) a scikit-learn (.joblib).

Extrae los parámetros de los archivos Parquet generados por PySpark 3.5
y construye objetos compatibles con la interfaz sklearn (predict / predict_proba).

Uso (desde la carpeta backend/):
    python -m scripts.convert_spark_models
"""

import logging
import sys
from pathlib import Path

import joblib
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Importar SparkRFPredictor desde app.ai para que joblib lo serialice
# con la ruta correcta (app.ai.spark_rf_predictor.SparkRFPredictor)
try:
    from app.ai.spark_rf_predictor import SparkRFPredictor
except ImportError:
    logger.error(
        "No se pudo importar SparkRFPredictor desde app.ai.spark_rf_predictor.\n"
        "Ejecuta este script desde la carpeta backend/ con el venv activo."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Rutas base
# Los modelos PySpark están en <repo>/models/, un nivel arriba de backend/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent          # backend/scripts/
_BACKEND_DIR = _SCRIPT_DIR.parent                      # backend/
_REPO_DIR = _BACKEND_DIR.parent                        # raíz del repo

MODELS_DIR = _REPO_DIR / "models"
LR_PARQUET_DIR = MODELS_DIR / "modelo_lr_empaquetado" / "data"
RF_PARQUET_DIR = MODELS_DIR / "modelo_rf_empaquetado" / "data"
LR_OUT = MODELS_DIR / "modelo_lr.joblib"
RF_OUT = MODELS_DIR / "modelo_rf.joblib"


# ---------------------------------------------------------------------------
# Conversión: Logistic Regression
# ---------------------------------------------------------------------------
def convert_lr(parquet_path: Path, out_path: Path) -> None:
    try:
        import pyarrow.parquet as pq
    except ImportError:
        logger.error("pyarrow no está instalado. Ejecuta: pip install pyarrow")
        sys.exit(1)

    logger.info("Leyendo modelo LR desde %s", parquet_path)
    tbl = pq.read_table(str(parquet_path))
    d = tbl.to_pydict()

    coef_values = d["coefficientMatrix"][0]["values"]
    intercept_value = d["interceptVector"][0]["values"][0]
    num_features = d["numFeatures"][0]
    num_classes = d["numClasses"][0]

    logger.info(
        "LR: numFeatures=%d, numClasses=%d, intercept=%.4f",
        num_features, num_classes, intercept_value,
    )

    from sklearn.linear_model import LogisticRegression

    lr = LogisticRegression()
    lr.classes_ = np.array([0, 1])
    lr.coef_ = np.array(coef_values, dtype=np.float64).reshape(1, -1)
    lr.intercept_ = np.array([intercept_value], dtype=np.float64)

    joblib.dump(lr, str(out_path))
    logger.info("Modelo LR guardado en %s", out_path)


# ---------------------------------------------------------------------------
# Conversión: Random Forest
# ---------------------------------------------------------------------------
def convert_rf(parquet_path: Path, out_path: Path) -> None:
    try:
        import pyarrow.parquet as pq
    except ImportError:
        logger.error("pyarrow no está instalado. Ejecuta: pip install pyarrow")
        sys.exit(1)

    logger.info("Leyendo modelo RF desde %s", parquet_path)
    tbl = pq.read_table(str(parquet_path))
    d = tbl.to_pydict()

    tree_ids = d["treeID"]
    node_data = d["nodeData"]

    num_trees = max(tree_ids) + 1
    logger.info("RF: %d árboles, %d nodos totales", num_trees, len(tree_ids))

    # Construir lista de árboles: cada árbol = dict {node_id: node_info}
    trees: list[dict] = [{} for _ in range(num_trees)]

    for i, tree_id in enumerate(tree_ids):
        nd = node_data[i]
        node_id = nd["id"]
        left_child = nd["leftChild"]
        right_child = nd["rightChild"]

        split = nd.get("split")
        if split and left_child >= 0:
            feature_idx = split["featureIndex"]
            # threshold es el primer elemento de leftCategoriesOrThreshold
            thresholds = split.get("leftCategoriesOrThreshold") or []
            threshold = float(thresholds[0]) if thresholds else 0.0
        else:
            feature_idx = -1
            threshold = -2.0

        # impurityStats contiene conteos de clase [count_0, count_1]
        imp_stats = nd.get("impurityStats") or [1.0, 0.0]
        total = sum(imp_stats) if sum(imp_stats) > 0 else 1.0
        proba = [s / total for s in imp_stats]

        trees[tree_id][node_id] = {
            "feature": feature_idx,
            "threshold": threshold,
            "left": left_child,
            "right": right_child,
            "proba": proba,
        }

    predictor = SparkRFPredictor(trees=trees, n_classes=2)
    joblib.dump(predictor, str(out_path))
    logger.info("Modelo RF guardado en %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def find_parquet(directory: Path) -> Path:
    """Retorna el primer archivo .parquet en el directorio."""
    matches = list(directory.glob("*.parquet"))
    if not matches:
        # Busca también con nombres que incluyan punto al inicio (archivos ocultos)
        matches = [
            p for p in directory.iterdir()
            if p.suffix == ".parquet" or p.name.endswith(".snappy.parquet")
        ]
    if not matches:
        raise FileNotFoundError(
            f"No se encontró ningún archivo .parquet en {directory}"
        )
    return matches[0]


def main() -> None:
    # Verificar que los directorios de modelos existen
    if not LR_PARQUET_DIR.is_dir():
        logger.error(
            "Directorio LR no encontrado: %s\n"
            "Asegúrate de ejecutar este script desde la carpeta backend/",
            LR_PARQUET_DIR,
        )
        sys.exit(1)

    if not RF_PARQUET_DIR.is_dir():
        logger.error(
            "Directorio RF no encontrado: %s\n"
            "Asegúrate de ejecutar este script desde la carpeta backend/",
            RF_PARQUET_DIR,
        )
        sys.exit(1)

    # Convertir LR
    try:
        lr_parquet = find_parquet(LR_PARQUET_DIR)
        convert_lr(lr_parquet, LR_OUT)
    except Exception:
        logger.exception("Falló la conversión del modelo LR")

    # Convertir RF
    try:
        rf_parquet = find_parquet(RF_PARQUET_DIR)
        convert_rf(rf_parquet, RF_OUT)
    except Exception:
        logger.exception("Falló la conversión del modelo RF")

    logger.info(
        "\nConversión completada.\n"
        "  LR  → %s\n"
        "  RF  → %s\n"
        "Reinicia uvicorn para cargar los modelos.",
        LR_OUT, RF_OUT,
    )


if __name__ == "__main__":
    main()
