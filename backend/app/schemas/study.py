from datetime import datetime

from pydantic import BaseModel, Field


class StudyCreate(BaseModel):
    patient_id: int
    appointment_id: int | None = None
    study_instance_uid: str | None = None
    modality: str = Field(default="CT", max_length=32)
    description: str | None = None
    image_storage_key: str | None = Field(None, max_length=512)


class StudyUpdate(BaseModel):
    study_instance_uid: str | None = None
    modality: str | None = Field(None, max_length=32)
    description: str | None = None
    image_storage_key: str | None = Field(None, max_length=512)
    appointment_id: int | None = None


class StudyRead(BaseModel):
    id: int
    patient_id: int
    appointment_id: int | None
    study_instance_uid: str | None
    modality: str
    description: str | None
    image_storage_key: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
