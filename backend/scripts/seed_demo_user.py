"""
Crea usuarios de demostración si no existen (incl. usuario dual secretaria + médico).

Uso: desde `backend/`:  python -m scripts.seed_demo_user
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.session import SessionLocal
from app.models import UserRole
from app.schemas.user import UserCreate
from app.services.role_service import RoleService
from app.services.user_service import UserService

DEMO_USERS: list[tuple[UserCreate, tuple[str, ...]]] = [
    (
        UserCreate(
            email="clinico@demo.example",
            password="Demo1234!",
            full_name="Usuario demo clínico",
            role="clinician",
        ),
        ("clinician",),
    ),
    (
        UserCreate(
            email="demo@hospital.com",
            password="demo1234",
            full_name="Dr. Carlos Mendez",
            role="clinician",
        ),
        ("clinician",),
    ),
    (
        UserCreate(
            email="secretaria@hospital.com",
            password="demo1234",
            full_name="Ana Torres",
            role="secretaria",
        ),
        ("secretaria",),
    ),
    (
        UserCreate(
            email="dual@hospital.com",
            password="demo12345",
            full_name="Demo Secretaría / Médico",
            role="clinician",
        ),
        ("clinician", "secretaria"),
    ),
]


def _ensure_roles(db: Session, user_id: int, roles: tuple[str, ...]) -> None:
    for r in roles:
        exists = (
            db.query(UserRole.id)
            .filter(UserRole.user_id == user_id, UserRole.role == r)
            .first()
        )
        if not exists:
            db.add(UserRole(user_id=user_id, role=r))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        for spec, extra_roles in DEMO_USERS:
            u = UserService.get_by_email(db, spec.email)
            if not u:
                u = UserService.create(db, spec)
                print("Creado usuario demo id=%s email=%s" % (u.id, u.email))
            elif not verify_password(spec.password, u.hashed_password):
                # Usuario existente con contraseña distinta a la demo documentada
                u.hashed_password = get_password_hash(spec.password)
                u.role = spec.role
                RoleService.sync_from_primary_role_uncommitted(db, u.id, spec.role)
                db.commit()
                db.refresh(u)
                print(
                    "Contraseña y rol primario actualizados para %s "
                    "(coincide con credenciales demo del proyecto)"
                    % spec.email
                )
            _ensure_roles(db, u.id, extra_roles)
        print(
            "\nUsuario DUAL (conmutador UI): dual@hospital.com / demo12345 "
            "— roles clinician + secretaria"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
