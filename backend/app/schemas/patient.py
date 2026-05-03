from datetime import date, datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    external_ref: str | None = None
    display_name: str = Field(min_length=1, max_length=255)
    birth_date: date | None = None
    notes: str | None = None


class PatientUpdate(BaseModel):
    external_ref: str | None = None
    display_name: str | None = Field(None, min_length=1, max_length=255)
    birth_date: date | None = None
    notes: str | None = None


class PatientRead(BaseModel):
    id: int
    external_ref: str | None
    display_name: str
    birth_date: date | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
