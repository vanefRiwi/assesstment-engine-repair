from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from business_service.domain.entities.repair_order import RepairOrder, StatusHistoryEntry
from business_service.domain.value_objects.statuses import RepairStatus


@dataclass(frozen=True)
class RepairOrderFilters:
    status: RepairStatus | None = None
    client_id: UUID | None = None
    engine_id: UUID | None = None
    search: str | None = None
    limit: int = 50
    offset: int = 0


class RepairOrderRepository(ABC):
    @abstractmethod
    def next_order_number(self) -> str:
        """Returns a unique human-readable number; must be safe under concurrent requests."""

    @abstractmethod
    def get(self, order_id: UUID) -> RepairOrder | None: ...

    @abstractmethod
    def search(self, filters: RepairOrderFilters) -> tuple[list[RepairOrder], int]: ...

    @abstractmethod
    def add(self, order: RepairOrder, history: StatusHistoryEntry) -> RepairOrder: ...

    @abstractmethod
    def update(self, order: RepairOrder, history: StatusHistoryEntry | None = None) -> RepairOrder: ...

    @abstractmethod
    def history(self, order_id: UUID) -> list[StatusHistoryEntry]: ...

    @abstractmethod
    def count_by_status(self) -> dict[RepairStatus, int]: ...

    @abstractmethod
    def exists_for_engine(self, engine_id: UUID) -> bool: ...
