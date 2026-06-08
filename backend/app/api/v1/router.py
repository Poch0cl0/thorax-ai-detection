from fastapi import APIRouter

from app.api.v1.endpoints import (
    appointments,
    auth,
    health,
    patients,
    predictions,
    scan,
    studies,
    test_tables,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patients.router)
api_router.include_router(studies.router)
api_router.include_router(appointments.router)
api_router.include_router(predictions.router)
api_router.include_router(scan.router)
api_router.include_router(test_tables.router)
