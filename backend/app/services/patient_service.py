from sqlalchemy.orm import Session

from app.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    @staticmethod
    def create(db: Session, data: PatientCreate) -> Patient:
        p = Patient(
            external_ref=data.external_ref,
            display_name=data.display_name,
            birth_date=data.birth_date,
            notes=data.notes,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p

    @staticmethod
    def get(db: Session, patient_id: int) -> Patient | None:
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> list[Patient]:
        return (
            db.query(Patient).order_by(Patient.id.desc()).offset(skip).limit(limit).all()
        )

    @staticmethod
    def update(db: Session, patient_id: int, data: PatientUpdate) -> Patient | None:
        p = PatientService.get(db, patient_id)
        if not p:
            return None
        payload = data.model_dump(exclude_unset=True)
        for k, v in payload.items():
            setattr(p, k, v)
        db.commit()
        db.refresh(p)
        return p
