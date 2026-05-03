from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"), index=True)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    model_version: Mapped[str] = mapped_column(String(64), default="stub-0.1.0")
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    finding_label: Mapped[str] = mapped_column(String(128))
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    study: Mapped["Study"] = relationship("Study", back_populates="predictions")
    author: Mapped["User | None"] = relationship("User", back_populates="predictions")
