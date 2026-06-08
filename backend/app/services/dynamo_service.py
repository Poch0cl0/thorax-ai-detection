"""
Servicio para guardar y consultar diagnósticos en AWS DynamoDB.

Tabla esperada: thorax_diagnoses
  - Partition key: diagnosis_id  (String)
  - No sort key requerida.

Si las credenciales no están configuradas, las operaciones fallan
con un error claro en lugar de crashear silenciosamente.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_table():
    """Retorna el recurso de tabla DynamoDB. Lanza ValueError si no hay credenciales."""
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        raise ValueError(
            "Las credenciales de AWS no están configuradas. "
            "Agrega AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY al archivo .env"
        )

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return dynamodb.Table(settings.DYNAMO_TABLE_NAME)


def save_diagnosis(diagnosis: dict[str, Any]) -> dict[str, Any]:
    """
    Guarda un diagnóstico en DynamoDB.

    El documento guardado incluye todos los campos del diagnóstico
    más un timestamp ISO 8601 de cuándo fue indexado en Dynamo.

    Args:
        diagnosis: Diccionario con los datos del diagnóstico (viene del INSERT en RDS).

    Returns:
        El mismo diccionario enriquecido con `dynamo_indexed_at`.

    Raises:
        ValueError: si las credenciales no están configuradas.
        RuntimeError: si DynamoDB rechaza la operación.
    """
    table = _get_table()

    item: dict[str, Any] = {
        "diagnosis_id": str(diagnosis["id"]),
        "patient_id": str(diagnosis.get("patient_id", "")),
        "prediction_label": diagnosis.get("prediction_label") or "unknown",
        "lr_probability": str(diagnosis.get("lr_probability") or ""),
        "rf_probability": str(diagnosis.get("rf_probability") or ""),
        "image_url": diagnosis.get("image_url") or "",
        "rds_created_at": str(diagnosis.get("created_at", "")),
        "dynamo_indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    # Incluir campos extra que vengan del endpoint enriquecido
    for field in ("risk_level", "confidence_percent", "recommendation"):
        if field in diagnosis:
            item[field] = str(diagnosis[field])

    try:
        table.put_item(Item=item)
        logger.info("Diagnóstico id=%s guardado en DynamoDB tabla=%s", item["diagnosis_id"], settings.DYNAMO_TABLE_NAME)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Error al guardar diagnóstico en DynamoDB")
        raise RuntimeError(f"DynamoDB error: {exc}") from exc

    return {**diagnosis, "dynamo_indexed_at": item["dynamo_indexed_at"]}


def get_diagnosis_from_dynamo(diagnosis_id: int | str) -> dict[str, Any] | None:
    """
    Obtiene un diagnóstico de DynamoDB por su ID.

    Returns:
        Diccionario con el item o None si no existe.
    """
    table = _get_table()

    try:
        response = table.get_item(Key={"diagnosis_id": str(diagnosis_id)})
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Error al leer diagnóstico de DynamoDB")
        raise RuntimeError(f"DynamoDB error: {exc}") from exc

    return response.get("Item")


def list_diagnoses_by_patient_dynamo(patient_id: int | str) -> list[dict[str, Any]]:
    """
    Escanea la tabla DynamoDB filtrando por patient_id.

    Nota: usa Scan (no Query) porque patient_id no es la partition key.
    Para producción de alto volumen se recomienda un GSI sobre patient_id.
    """
    table = _get_table()

    try:
        response = table.scan(
            FilterExpression=Key("patient_id").eq(str(patient_id))
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Error al escanear DynamoDB por patient_id")
        raise RuntimeError(f"DynamoDB error: {exc}") from exc

    return response.get("Items", [])


def ensure_table_exists() -> bool:
    """
    Verifica si la tabla DynamoDB existe. Si no, la crea automáticamente.

    Returns:
        True si la tabla ya existía, False si fue creada ahora.
    """
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        raise ValueError("Credenciales AWS no configuradas.")

    client = boto3.client(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        client.describe_table(TableName=settings.DYNAMO_TABLE_NAME)
        logger.info("Tabla DynamoDB '%s' ya existe.", settings.DYNAMO_TABLE_NAME)
        return True
    except client.exceptions.ResourceNotFoundException:
        pass

    logger.info("Creando tabla DynamoDB '%s'...", settings.DYNAMO_TABLE_NAME)
    client.create_table(
        TableName=settings.DYNAMO_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "diagnosis_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "diagnosis_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=settings.DYNAMO_TABLE_NAME)
    logger.info("Tabla DynamoDB '%s' creada exitosamente.", settings.DYNAMO_TABLE_NAME)
    return False
