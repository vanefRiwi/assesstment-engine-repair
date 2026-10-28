from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from business_service.domain.entities.engine import Engine


@dataclass(frozen=True)
class EngineFilters:
    search: str | None = None
    client_id: UUID | None = None
    is_active: bool | None = None
    limit: int = 50
    offset: int = 0


class EngineRepository(ABC):
    @abstractmethod
    def get(self, engine_id: UUID) -> Engine | None: ...

    @abstractmethod
    def get_by_serial(self, serial_number: str) -> Engine | None: ...

    @abstractmethod
    def search(self, filters: EngineFilters) -> tuple[list[Engine], int]: ...

    @abstractmethod
    def add(self, engine: Engine) -> Engine: ...

    @abstractmethod
    def update(self, engine: Engine) -> Engine: ...
