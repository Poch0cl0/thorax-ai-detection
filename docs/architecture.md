# Arquitectura Thorax AI

## Vista general

El sistema separa la API transaccional (FastAPI), la interfaz web (React + TypeScript), la persistencia (PostgreSQL o SQLite en desarrollo) y el módulo de inferencia (carpeta `app/ai`).

- **Routers** (`app/api/v1/endpoints/`): HTTP, autenticación OAuth2 con JWT, validación con Pydantic.
- **Servicios** (`app/services/`): reglas de negocio y orquestación.
- **Modelos ORM** (`app/models/`): usuarios, pacientes, estudios, predicciones y auditoría.
- **Integraciones** (`app/integrations/`): contrato HIS/RIS/PACS; implementación stub por defecto.
- **IA** (`app/ai/`): carga de modelo opcional, preprocesado e inferencia (simulada si no hay `MODEL_PATH`).
- **Auditoría** (`app/audit/`): registro de eventos relevantes (p. ej. creación de predicción).

## Datos sensibles

Reducir PHI al mínimo necesario: pseudónimos en `display_name`, referencias DICOM/PACS en `image_storage_key` y `study_instance_uid`, sin almacenar imágenes completas en la API salvo decisión explícita de despliegue.

## Despliegue con Docker

`docker-compose` levanta PostgreSQL, backend (migraciones Alembic + Uvicorn) y frontend (Nginx sirviendo el build estático y proxy `/api` al backend). Las variables sensibles deben inyectarse por entorno, no en el repositorio.
