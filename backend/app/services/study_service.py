from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Appointment, Patient, Study
from app.schemas.study import StudyCreate, StudyUpdate
from app.utils.file_handler import ensure_parent_dir, safe_suffix


class StudyService:
    @staticmethod
    def _ensure_appointment_patient_consistency(
        db: Session,
        *,
        patient_id: int,
        appointment_id: int | None,
    ) -> None:
        if appointment_id is None:
            return
        ap = db.get(Appointment, appointment_id)
        if not ap:
            raise ValueError("La cita no existe")
        if ap.patient_id != patient_id:
            raise ValueError("La cita no corresponde al paciente del estudio")

    @staticmethod
    def create(db: Session, data: StudyCreate) -> Study:
        p = db.get(Patient, data.patient_id)
        if not p:
            raise ValueError("Paciente no encontrado")
        StudyService._ensure_appointment_patient_consistency(
            db,
            patient_id=data.patient_id,
            appointment_id=data.appointment_id,
        )
        s = Study(
            patient_id=data.patient_id,
            appointment_id=data.appointment_id,
            study_instance_uid=data.study_instance_uid,
            modality=data.modality,
            description=data.description,
            image_storage_key=data.image_storage_key,
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def create_with_upload(
        db: Session,
        *,
        patient_id: int,
        appointment_id: int | None,
        modality: str,
        description: str | None,
        file_content: bytes,
        original_filename: str,
    ) -> Study:
        p = db.get(Patient, patient_id)
        if not p:
            raise ValueError("Paciente no encontrado")
        StudyService._ensure_appointment_patient_consistency(
            db,
            patient_id=patient_id,
            appointment_id=appointment_id,
        )

        suf = safe_suffix(original_filename) or ".bin"
        s = Study(
            patient_id=patient_id,
            appointment_id=appointment_id,
            study_instance_uid=None,
            modality=modality,
            description=description,
            image_storage_key=None,
        )
        db.add(s)
        db.flush()

        relative = f"studies/{s.id}{suf}"
        root = Path(settings.UPLOAD_ROOT)
        abs_path = (root / relative).resolve()
        ensure_parent_dir(abs_path)
        abs_path.write_bytes(file_content)

        s.image_storage_key = relative
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def get(db: Session, study_id: int) -> Study | None:
        return db.query(Study).filter(Study.id == study_id).first()

    @staticmethod
    def list_for_patient(db: Session, patient_id: int) -> list[Study]:
        return (
            db.query(Study)
            .filter(Study.patient_id == patient_id)
            .order_by(Study.id.desc())
            .all()
        )

    @staticmethod
    def update(db: Session, study_id: int, data: StudyUpdate) -> Study | None:
        s = StudyService.get(db, study_id)
        if not s:
            return None
        payload = data.model_dump(exclude_unset=True)
        for k, v in payload.items():
            setattr(s, k, v)
        db.commit()
        db.refresh(s)
        return s
