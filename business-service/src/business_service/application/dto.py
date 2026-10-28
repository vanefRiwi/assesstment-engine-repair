"""Plain input objects for use cases, independent of HTTP schemas."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class CreateClientInput:
    name: str
    document_type: str
    document_number: str
    email: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class UpdateClientInput:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class CreateEngineInput:
    serial_number: str
    manufacturer: str
    model: str
    engine_type: str
    client_id: UUID
    capacity: str | None = None


@dataclass(frozen=True)
class UpdateEngineInput:
    manufacturer: str | None = None
    model: str | None = None
    engine_type: str | None = None
    capacity: str | None = None
    client_id: UUID | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class CreateRepairOrderInput:
    engine_id: UUID
    received_at: datetime
    reported_problem: str
    client_id: UUID | None = None
    technical_diagnosis: str | None = None
    repair_description: str | None = None
    technician_name: str | None = None
    estimated_delivery_at: datetime | None = None
    observations: str | None = None


@dataclass(frozen=True)
class ChangeStatusInput:
    status: str
    observations: str | None = None
    technical_diagnosis: str | None = None
    repair_description: str | None = None
    technician_name: str | None = None
    estimated_delivery_at: datetime | None = None
