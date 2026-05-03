from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HISClientProtocol(Protocol):
    """Contrato para integración con HIS/RIS/PACS (REST, FHIR, HL7 v2, etc.)."""

    def fetch_patient_summary(self, external_id: str) -> dict[str, Any]:
        """Devuelve metadatos mínimos del paciente en el sistema fuente."""
        ...

    def notify_study_registered(self, study_uid: str, payload: dict[str, Any]) -> None:
        """Callback opcional tras registrar un estudio localmente."""
        ...


class StubHISClient:
    """Implementación de desarrollo sin red externa."""

    def fetch_patient_summary(self, external_id: str) -> dict[str, Any]:
        return {
            "external_id": external_id,
            "source": "stub",
            "display_name": None,
        }

    def notify_study_registered(self, study_uid: str, payload: dict[str, Any]) -> None:
        return None
