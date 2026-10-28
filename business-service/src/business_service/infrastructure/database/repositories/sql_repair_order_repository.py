from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, select

from business_service.domain.entities.repair_order import RepairOrder, StatusHistoryEntry
from business_service.domain.repositories.repair_order_repository import (
    RepairOrderFilters,
    RepairOrderRepository,
)
from business_service.domain.time import utc_now
from business_service.domain.value_objects.statuses import ApprovalStatus, RepairStatus
from business_service.infrastructure.database.models.tables import (
    RepairOrderTable,
    RepairStatusHistoryTable,
    order_number_sequence,
)
from business_service.infrastructure.database.repositories.errors import translate_integrity_error


def _to_domain(row: RepairOrderTable) -> RepairOrder:
    data = row.model_dump()
    data["status"] = RepairStatus(data["status"])
    data["approval_status"] = ApprovalStatus(data["approval_status"])
    return RepairOrder(**data)


def _history_to_domain(row: RepairStatusHistoryTable) -> StatusHistoryEntry:
    data = row.model_dump()
    data["status"] = RepairStatus(data["status"])
    return StatusHistoryEntry(**data)


def _history_row(entry: StatusHistoryEntry) -> RepairStatusHistoryTable:
    return RepairStatusHistoryTable(**{**vars(entry), "status": entry.status.value})


def _order_values(order: RepairOrder) -> dict:
    return {**vars(order), "status": order.status.value, "approval_status": order.approval_status.value}


class SqlRepairOrderRepository(RepairOrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def next_order_number(self) -> str:
        # A database sequence never hands out the same value twice, even under concurrency.
        value = self.session.execute(order_number_sequence.next_value()).scalar_one()
        return f"REP-{utc_now().year}-{value:06d}"

    def get(self, order_id: UUID) -> RepairOrder | None:
        row = self.session.get(RepairOrderTable, order_id)
        return _to_domain(row) if row else None

    def search(self, filters: RepairOrderFilters) -> tuple[list[RepairOrder], int]:
        statement = select(RepairOrderTable)
        if filters.status:
            statement = statement.where(RepairOrderTable.status == filters.status.value)
        if filters.client_id:
            statement = statement.where(RepairOrderTable.client_id == filters.client_id)
        if filters.engine_id:
            statement = statement.where(RepairOrderTable.engine_id == filters.engine_id)
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(
                    RepairOrderTable.order_number.ilike(pattern),  # type: ignore[union-attr]
                    RepairOrderTable.reported_problem.ilike(pattern),  # type: ignore[union-attr]
                    RepairOrderTable.technician_name.ilike(pattern),  # type: ignore[union-attr]
                )
            )

        total = self.session.exec(select(func.count()).select_from(statement.subquery())).one()
        rows = self.session.exec(
            statement.order_by(RepairOrderTable.created_at.desc())  # type: ignore[attr-defined]
            .offset(filters.offset)
            .limit(filters.limit)
        ).all()
        return [_to_domain(row) for row in rows], total

    def add(self, order: RepairOrder, history: StatusHistoryEntry) -> RepairOrder:
        self.session.add(RepairOrderTable(**_order_values(order)))
        with translate_integrity_error():
            self.session.flush()
        self.session.add(_history_row(history))
        self.session.flush()
        return order

    def update(self, order: RepairOrder, history: StatusHistoryEntry | None = None) -> RepairOrder:
        row = self.session.get(RepairOrderTable, order.id)
        assert row is not None
        row.sqlmodel_update(_order_values(order))
        if history is not None:
            self.session.add(_history_row(history))
        with translate_integrity_error():
            self.session.flush()
        return order

    def history(self, order_id: UUID) -> list[StatusHistoryEntry]:
        rows = self.session.exec(
            select(RepairStatusHistoryTable)
            .where(RepairStatusHistoryTable.repair_order_id == order_id)
            .order_by(RepairStatusHistoryTable.changed_at)  # type: ignore[arg-type]
        ).all()
        return [_history_to_domain(row) for row in rows]

    def count_by_status(self) -> dict[RepairStatus, int]:
        rows = self.session.exec(select(RepairOrderTable.status, func.count()).group_by(RepairOrderTable.status)).all()
        return {RepairStatus(status): count for status, count in rows}

    def exists_for_engine(self, engine_id: UUID) -> bool:
        statement = select(RepairOrderTable.id).where(RepairOrderTable.engine_id == engine_id).limit(1)
        return self.session.exec(statement).first() is not None
