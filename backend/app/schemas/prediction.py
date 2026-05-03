from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    """Entrada para ejecutar inferencia sobre un estudio existente."""

    study_id: int
    finding_hint: str | None = Field(
        None, description="Opcional; no sustituye la inferencia del modelo"
    )


class PredictionRead(BaseModel):
    id: int
    study_id: int
    created_by_id: int | None
    model_version: str
    risk_score: float | None
    finding_label: str
    details: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
