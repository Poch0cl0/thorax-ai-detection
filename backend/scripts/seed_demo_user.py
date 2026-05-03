"""
Crea un usuario de demostración si no existe.
Uso: desde `backend/`:  python -m scripts.seed_demo_user
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.services.user_service import UserService

DEMO_EMAIL = "clinico@demo.example"
DEMO_PASSWORD = "Demo1234!"


def main() -> None:
    db = SessionLocal()
    try:
        if UserService.get_by_email(db, DEMO_EMAIL):
            print("Usuario demo ya existe:", DEMO_EMAIL)
            return
        user = UserService.create(
            db,
            UserCreate(
                email=DEMO_EMAIL,
                password=DEMO_PASSWORD,
                full_name="Usuario demo",
                role="clinician",
            ),
        )
        print("Creado usuario demo id=%s email=%s" % (user.id, user.email))
    finally:
        db.close()


if __name__ == "__main__":
    main()
