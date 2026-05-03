from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditService:
    @staticmethod
    def add_entry(
        db: Session,
        *,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        user_id: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=details,
        )
        db.add(entry)
        return entry
