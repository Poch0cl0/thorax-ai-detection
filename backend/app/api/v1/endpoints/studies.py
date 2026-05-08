from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models import User
from app.schemas.study import StudyCreate, StudyRead, StudyUpdate
from app.services.role_service import RoleService
from app.services.study_service import StudyService

router = APIRouter(prefix="/studies", tags=["studies"])

DoctorOrAdmin = Annotated[
    User,
    Depends(require_roles("clinician", "admin")),
]


def _doctor_or_specialist_roles(db: Session, user_id: int) -> bool:
    return RoleService.user_has_any(db, user_id, {"clinician", "admin"})


@router.post("", response_model=StudyRead, status_code=status.HTTP_201_CREATED)
def create_study(
    data: StudyCreate,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> object:
    if not _doctor_or_specialist_roles(db, current.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Se requiere rol de médico o administrador para crear estudios."
            ),
        )
    try:
        return StudyService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/with-image",
    response_model=StudyRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_study_with_image(
    db: Annotated[Session, Depends(get_db)],
    current: DoctorOrAdmin,
    patient_id: Annotated[int, Form()],
    modality: Annotated[str, Form()] = "radiografia",
    appointment_id: Annotated[int | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    file: UploadFile = File(...),
) -> object:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Archivo vacío")

    mime = file.content_type or ""
    allowed = mime.startswith("image/") if mime else True
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sólo archivos imagen típicos (rx jpg/png) en modo demo.",
        )

    try:
        return StudyService.create_with_upload(
            db,
            patient_id=patient_id,
            appointment_id=appointment_id,
            modality=modality[:32],
            description=description,
            file_content=content,
            original_filename=file.filename or "upload.bin",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/patient/{patient_id}", response_model=list[StudyRead])
def list_by_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list:
    return StudyService.list_for_patient(db, patient_id)


@router.get("/{study_id}", response_model=StudyRead)
def get_study(
    study_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    s = StudyService.get(db, study_id)
    if not s:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return s


@router.patch("/{study_id}", response_model=StudyRead)
def update_study(
    study_id: int,
    data: StudyUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    s = StudyService.update(db, study_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return s
