# Thorax AI Detection

Sistema clínico de apoyo con API FastAPI, frontend React (TypeScript) e inferencia torácica (modelo real opcional vía `MODEL_PATH`).

## Requisitos

- Python 3.12+ (backend)
- Node 22+ (frontend)

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy ..\.env.example .env   # opcional; por defecto SQLite local
alembic upgrade head
python -m scripts.seed_demo_user
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Usuario demo (tras seed): `clinico@demo.example` / `Demo1234!`

Documentación interactiva: `http://127.0.0.1:8000/docs`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Por defecto el cliente usa `http://127.0.0.1:8000`. Para otra URL: variable `VITE_API_BASE_URL` en `.env` del frontend.

## Docker

Desde la raíz del repositorio:

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- UI con proxy Nginx: `http://localhost` (el navegador llama a `/api/...` en el mismo origen)

Copiar `.env.example` a `.env` y definir `SECRET_KEY` para entornos reales.

## Tests backend

```bash
cd backend
pytest tests -q
```
"# thorax-ai-detection" 
