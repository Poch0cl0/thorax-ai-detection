from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.prediction import PredictionCreate, PredictionRead
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=PredictionRead, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    data: PredictionCreate,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> object:
    try:
        return await PredictionService.run_and_store(
            db, data, user_id=current.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e)) from e


@router.get("/study/{study_id}", response_model=list[PredictionRead])
def list_for_study(
    study_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list:
    return PredictionService.list_for_study(db, study_id)


@router.get("/{prediction_id}", response_model=PredictionRead)
def get_prediction(
    prediction_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> object:
    p = PredictionService.get(db, prediction_id)
    if not p:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")
    return p
