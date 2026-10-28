"""Initial business schema: clients, engines, repair orders and status history.

Revision ID: 0001
Revises:
Create Date: 2026-10-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

REPAIR_STATUSES = "'RECEIVED','IN_DIAGNOSIS','AWAITING_APPROVAL','IN_REPAIR','IN_TESTING','COMPLETED','DELIVERED'"
APPROVAL_STATUSES = "'NOT_REQUIRED','PENDING','APPROVED','REJECTED'"


def _ts(name: str, nullable: bool = False) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("document_type", sa.String(20), nullable=False),
        sa.Column("document_number", sa.String(40), nullable=False),
        sa.Column("email", sa.String(254)),
        sa.Column("phone", sa.String(30)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        _ts("created_at"),
        _ts("updated_at"),
        sa.UniqueConstraint("document_type", "document_number", name="uq_clients_document"),
    )

    op.create_table(
        "engines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("serial_number", sa.String(100), nullable=False),
        sa.Column("manufacturer", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("engine_type", sa.String(60), nullable=False),
        sa.Column("capacity", sa.String(60)),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("clients.id"), nullable=False),
        _ts("registered_at"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        _ts("created_at"),
        _ts("updated_at"),
        sa.UniqueConstraint("serial_number", name="uq_engines_serial_number"),
        sa.UniqueConstraint("id", "client_id", name="uq_engines_id_client"),
    )
    op.create_index("ix_engines_client_id", "engines", ["client_id"])

    op.execute("CREATE SEQUENCE repair_order_number_seq")
    op.create_table(
        "repair_orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("order_number", sa.String(30), nullable=False),
        sa.Column("engine_id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        _ts("received_at"),
        sa.Column("reported_problem", sa.Text(), nullable=False),
        sa.Column("technical_diagnosis", sa.Text()),
        sa.Column("repair_description", sa.Text()),
        sa.Column("technician_name", sa.String(120)),
        _ts("estimated_delivery_at", nullable=True),
        _ts("actual_delivery_at", nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("approval_status", sa.String(20), nullable=False, server_default="NOT_REQUIRED"),
        _ts("approved_at", nullable=True),
        sa.Column("approval_notes", sa.Text()),
        sa.Column("observations", sa.Text()),
        _ts("created_at"),
        _ts("updated_at"),
        sa.UniqueConstraint("order_number", name="uq_repair_orders_order_number"),
        sa.ForeignKeyConstraint(
            ["engine_id", "client_id"],
            ["engines.id", "engines.client_id"],
            name="fk_repair_orders_engine_client",
        ),
        sa.CheckConstraint(f"status IN ({REPAIR_STATUSES})", name="ck_repair_orders_status"),
        sa.CheckConstraint(f"approval_status IN ({APPROVAL_STATUSES})", name="ck_repair_orders_approval_status"),
        sa.CheckConstraint("approved_at IS NULL OR approval_status = 'APPROVED'", name="ck_repair_orders_approved_at"),
    )
    op.create_index("ix_repair_orders_status", "repair_orders", ["status"])
    op.create_index("ix_repair_orders_engine_id", "repair_orders", ["engine_id"])
    op.create_index("ix_repair_orders_client_id", "repair_orders", ["client_id"])

    op.create_table(
        "repair_status_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("repair_order_id", sa.Uuid(), sa.ForeignKey("repair_orders.id"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("changed_by", sa.Uuid()),
        _ts("changed_at"),
        sa.Column("observations", sa.Text()),
        sa.CheckConstraint(f"status IN ({REPAIR_STATUSES})", name="ck_repair_status_history_status"),
    )
    op.create_index(
        "ix_repair_status_history_order_changed", "repair_status_history", ["repair_order_id", "changed_at"]
    )


def downgrade() -> None:
    op.drop_table("repair_status_history")
    op.drop_table("repair_orders")
    op.execute("DROP SEQUENCE IF EXISTS repair_order_number_seq")
    op.drop_table("engines")
    op.drop_table("clients")
