import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación:
    - Startup: pre-carga los modelos PySpark ML.
    - Shutdown: cierra la SparkSession de forma ordenada.
    """
    # --- Startup ---
    logger.info("Iniciando Thorax AI — cargando modelos…")
    try:
        from app.ai.model_loader import load_all_models
        load_all_models()
        logger.info("Modelos cargados exitosamente")
    except Exception:
        logger.exception(
            "Error al cargar modelos ML — la inferencia simulada "
            "seguirá disponible"
        )

    yield

    # --- Shutdown ---
    logger.info("Apagando Thorax AI…")
    try:
        from app.ai.model_loader import shutdown_spark
        shutdown_spark()
    except Exception:
        logger.exception("Error durante shutdown de Spark")


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
