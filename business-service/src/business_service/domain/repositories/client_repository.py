from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from business_service.domain.entities.client import Client


@dataclass(frozen=True)
class ClientFilters:
    search: str | None = None
    is_active: bool | None = None
    limit: int = 50
    offset: int = 0


class ClientRepository(ABC):
    @abstractmethod
    def get(self, client_id: UUID) -> Client | None: ...

    @abstractmethod
    def get_by_document(self, document_type: str, document_number: str) -> Client | None: ...

    @abstractmethod
    def search(self, filters: ClientFilters) -> tuple[list[Client], int]: ...

    @abstractmethod
    def add(self, client: Client) -> Client: ...

    @abstractmethod
    def update(self, client: Client) -> Client: ...
