"""SQLModel persistence models. Only the infrastructure layer imports these."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Sequence,
    String,
    Text,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel

REPAIR_STATUSES = "'RECEIVED','IN_DIAGNOSIS','AWAITING_APPROVAL','IN_REPAIR','IN_TESTING','COMPLETED','DELIVERED'"
APPROVAL_STATUSES = "'NOT_REQUIRED','PENDING','APPROVED','REJECTED'"

order_number_sequence = Sequence("repair_order_number_seq")


def _timestamp(nullable: bool = False) -> Column:
    return Column(DateTime(timezone=True), nullable=nullable)


class ClientTable(SQLModel, table=True):
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("document_type", "document_number", name="uq_clients_document"),)

    id: UUID = Field(primary_key=True)
    name: str = Field(sa_column=Column(String(150), nullable=False))
    document_type: str = Field(sa_column=Column(String(20), nullable=False))
    document_number: str = Field(sa_column=Column(String(40), nullable=False))
    email: str | None = Field(default=None, sa_column=Column(String(254)))
    phone: str | None = Field(default=None, sa_column=Column(String(30)))
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(sa_column=_timestamp())
    updated_at: datetime = Field(sa_column=_timestamp())


class EngineTable(SQLModel, table=True):
    __tablename__ = "engines"
    __table_args__ = (
        UniqueConstraint("serial_number", name="uq_engines_serial_number"),
        UniqueConstraint("id", "client_id", name="uq_engines_id_client"),
        Index("ix_engines_client_id", "client_id"),
    )

    id: UUID = Field(primary_key=True)
    serial_number: str = Field(sa_column=Column(String(100), nullable=False))
    manufacturer: str = Field(sa_column=Column(String(100), nullable=False))
    model: str = Field(sa_column=Column(String(100), nullable=False))
    engine_type: str = Field(sa_column=Column(String(60), nullable=False))
    capacity: str | None = Field(default=None, sa_column=Column(String(60)))
    client_id: UUID = Field(foreign_key="clients.id", nullable=False)
    registered_at: datetime = Field(sa_column=_timestamp())
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(sa_column=_timestamp())
    updated_at: datetime = Field(sa_column=_timestamp())


class RepairOrderTable(SQLModel, table=True):
    __tablename__ = "repair_orders"
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_repair_orders_order_number"),
        # The order's client must be the engine's owner (composite FK).
        ForeignKeyConstraint(
            ["engine_id", "client_id"],
            ["engines.id", "engines.client_id"],
            name="fk_repair_orders_engine_client",
        ),
        Index("ix_repair_orders_status", "status"),
        Index("ix_repair_orders_engine_id", "engine_id"),
        Index("ix_repair_orders_client_id", "client_id"),
        CheckConstraint(f"status IN ({REPAIR_STATUSES})", name="ck_repair_orders_status"),
        CheckConstraint(f"approval_status IN ({APPROVAL_STATUSES})", name="ck_repair_orders_approval_status"),
        CheckConstraint("approved_at IS NULL OR approval_status = 'APPROVED'", name="ck_repair_orders_approved_at"),
    )

    id: UUID = Field(primary_key=True)
    order_number: str = Field(sa_column=Column(String(30), nullable=False))
    engine_id: UUID = Field(nullable=False)
    client_id: UUID = Field(nullable=False)
    received_at: datetime = Field(sa_column=_timestamp())
    reported_problem: str = Field(sa_column=Column(Text, nullable=False))
    technical_diagnosis: str | None = Field(default=None, sa_column=Column(Text))
    repair_description: str | None = Field(default=None, sa_column=Column(Text))
    technician_name: str | None = Field(default=None, sa_column=Column(String(120)))
    estimated_delivery_at: datetime | None = Field(default=None, sa_column=_timestamp(nullable=True))
    actual_delivery_at: datetime | None = Field(default=None, sa_column=_timestamp(nullable=True))
    status: str = Field(sa_column=Column(String(30), nullable=False))
    approval_status: str = Field(sa_column=Column(String(20), nullable=False))
    approved_at: datetime | None = Field(default=None, sa_column=_timestamp(nullable=True))
    approval_notes: str | None = Field(default=None, sa_column=Column(Text))
    observations: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(sa_column=_timestamp())
    updated_at: datetime = Field(sa_column=_timestamp())


class RepairStatusHistoryTable(SQLModel, table=True):
    __tablename__ = "repair_status_history"
    __table_args__ = (
        Index("ix_repair_status_history_order_changed", "repair_order_id", "changed_at"),
        CheckConstraint(f"status IN ({REPAIR_STATUSES})", name="ck_repair_status_history_status"),
    )

    id: UUID = Field(primary_key=True)
    repair_order_id: UUID = Field(foreign_key="repair_orders.id", nullable=False)
    status: str = Field(sa_column=Column(String(30), nullable=False))
    changed_by: UUID | None = Field(default=None)
    changed_at: datetime = Field(sa_column=_timestamp())
    observations: str | None = Field(default=None, sa_column=Column(Text))
