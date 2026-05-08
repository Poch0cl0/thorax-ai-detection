from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    study_instance_uid: Mapped[str | None] = mapped_column(String(128), index=True)
    modality: Mapped[str] = mapped_column(String(32), default="CT")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_storage_key: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )  # Ruta/UID en PACS o almacén de objetos
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="studies")
    appointment: Mapped["Appointment | None"] = relationship(
        "Appointment", back_populates="studies"
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction", back_populates="study"
    )
