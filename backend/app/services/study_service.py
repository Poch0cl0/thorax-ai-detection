from sqlalchemy.orm import Session

from app.models import Study
from app.schemas.study import StudyCreate, StudyUpdate


class StudyService:
    @staticmethod
    def create(db: Session, data: StudyCreate) -> Study:
        s = Study(
            patient_id=data.patient_id,
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
