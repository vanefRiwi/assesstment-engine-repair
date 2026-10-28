from dataclasses import replace
from uuid import UUID

from business_service.application.dto import CreateClientInput, Page, UpdateClientInput
from business_service.domain.entities.client import Client
from business_service.domain.exceptions import ConflictError, NotFoundError
from business_service.domain.repositories.client_repository import ClientFilters, ClientRepository
from business_service.domain.time import utc_now


def get_client_or_fail(clients: ClientRepository, client_id: UUID) -> Client:
    client = clients.get(client_id)
    if client is None:
        raise NotFoundError("Client not found.")
    return client


class CreateClient:
    def __init__(self, clients: ClientRepository) -> None:
        self.clients = clients

    def execute(self, data: CreateClientInput) -> Client:
        client = Client(
            name=data.name,
            document_type=data.document_type,
            document_number=data.document_number,
            email=data.email,
            phone=data.phone,
        )
        if self.clients.get_by_document(client.document_type, client.document_number):
            raise ConflictError("A client with this document already exists.")
        return self.clients.add(client)


class UpdateClient:
    def __init__(self, clients: ClientRepository) -> None:
        self.clients = clients

    def execute(self, client_id: UUID, data: UpdateClientInput) -> Client:
        client = get_client_or_fail(self.clients, client_id)
        changes = {key: value for key, value in vars(data).items() if value is not None}
        if not changes:
            return client
        updated = replace(client, **changes, updated_at=utc_now())
        return self.clients.update(updated)


class GetClient:
    def __init__(self, clients: ClientRepository) -> None:
        self.clients = clients

    def execute(self, client_id: UUID) -> Client:
        return get_client_or_fail(self.clients, client_id)


class ListClients:
    def __init__(self, clients: ClientRepository) -> None:
        self.clients = clients

    def execute(self, filters: ClientFilters) -> Page[Client]:
        items, total = self.clients.search(filters)
        return Page(items=items, total=total, limit=filters.limit, offset=filters.offset)
