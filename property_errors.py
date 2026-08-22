"""Capture grouped backend failures from a property-management workflow."""

import hashlib
import traceback
from dataclasses import dataclass

from infrai import infrai


@dataclass(frozen=True)
class PropertyEvent:
    property_id: str
    kind: str
    record_id: str


def error_group(event: PropertyEvent) -> str:
    """Use the property and business record kind as the grouping decision."""
    if event.kind not in {"maintenance", "tenant_document", "inspection"}:
        raise ValueError(f"unsupported property event kind: {event.kind}")
    return hashlib.sha256(f"property:{event.property_id}:{event.kind}".encode()).hexdigest()[:16]


def capture_backend_error(event: PropertyEvent, exc: Exception) -> dict:
    group = error_group(event)
    return infrai.errors.capture(
        title=f"{event.kind} backend error",
        message=str(exc),
        exception=traceback.format_exc(),
        level="error",
        fingerprint=["property-backend", group],
        context={
            "property_id": event.property_id,
            "record_id": event.record_id,
            "kind": event.kind,
        },
        idempotency_key=f"property-error:{event.property_id}:{event.record_id}",
    )


def record_backend_attempt(event: PropertyEvent, operation) -> dict:
    """Run one domain operation and capture its backend exception with context."""
    try:
        operation()
    except Exception as exc:
        return capture_backend_error(event, exc)
    return {"status": "ok", "group": error_group(event)}


if __name__ == "__main__":
    event = PropertyEvent("building-17", "inspection", "reminder-204")
    result = record_backend_attempt(event, lambda: (_ for _ in ()).throw(RuntimeError("reminder write failed")))
    print(f"Captured {event.kind} error for group {error_group(event)}")
    print(result)
