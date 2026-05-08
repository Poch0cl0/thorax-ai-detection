from datetime import datetime

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    patient_id: int
    attending_user_id: int = Field(
        ...,
        description="ID del usuario médico (rol clinician) asignado",
    )
    scheduled_at: datetime
    notes: str | None = None
    status: str = Field(default="pendiente", max_length=32)


class AppointmentUpdate(BaseModel):
    patient_id: int | None = None
    attending_user_id: int | None = None
    scheduled_at: datetime | None = None
    notes: str | None = None
    status: str | None = Field(None, max_length=32)


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    attending_user_id: int | None
    scheduled_at: datetime
    status: str
    notes: str | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
