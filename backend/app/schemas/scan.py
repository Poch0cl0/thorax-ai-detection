"""Esquemas para el análisis de imágenes de radiografía (scan)."""

from pydantic import BaseModel, Field


class ScanAnalysisResponse(BaseModel):
    """Resultado del análisis de una radiografía de tórax."""

    prediction: str = Field(
        ...,
        description="Predicción: 'cancer_detected' o 'no_cancer'",
        examples=["no_cancer"],
    )
    probability_cancer: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilidad de cáncer (0.0 a 1.0)",
    )
    probability_normal: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilidad de normalidad (0.0 a 1.0)",
    )
    risk_level: str = Field(
        ...,
        description="Nivel de riesgo: 'alto', 'moderado', 'bajo'",
        examples=["bajo"],
    )
    model_used: str = Field(
        ...,
        description="Identificador del modelo usado",
        examples=["random_forest"],
    )
    model_display_name: str = Field(
        ...,
        description="Nombre legible del modelo",
        examples=["Random Forest"],
    )
    model_version: str = Field(
        ...,
        description="Versión del modelo",
    )
    confidence_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confianza de la predicción en porcentaje",
    )
    recommendation: str = Field(
        ...,
        description="Recomendación clínica basada en el resultado",
    )
    disclaimer: str = Field(
        ...,
        description="Aviso médico-legal obligatorio",
    )


class ModelsInfoResponse(BaseModel):
    """Información sobre los modelos disponibles."""

    available_models: list[str] = Field(
        ...,
        description="Lista de modelos cargados y disponibles",
    )
    model_options: list[dict] = Field(
        ...,
        description="Opciones de modelo con etiquetas para UI",
    )
