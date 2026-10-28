from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from business_service.application.dto import CreateClientInput, UpdateClientInput
from business_service.application.use_cases.clients import CreateClient, GetClient, ListClients, UpdateClient
from business_service.domain.repositories.client_repository import ClientFilters
from business_service.presentation.api.dependencies.auth import CurrentUser
from business_service.presentation.api.dependencies.repositories import Clients
from business_service.presentation.api.schemas.clients import ClientCreate, ClientResponse, ClientUpdate
from business_service.presentation.api.schemas.common import PageResponse

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", status_code=201)
def create_client(body: ClientCreate, clients: Clients, _: CurrentUser, response: Response) -> ClientResponse:
    client = CreateClient(clients).execute(CreateClientInput(**body.model_dump()))
    response.headers["Location"] = f"/api/v1/clients/{client.id}"
    return ClientResponse.model_validate(client)


@router.get("")
def list_clients(
    clients: Clients,
    _: CurrentUser,
    q: Annotated[str | None, Query(max_length=100, description="Name or document number")] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PageResponse[ClientResponse]:
    page = ListClients(clients).execute(ClientFilters(search=q, is_active=is_active, limit=limit, offset=offset))
    return PageResponse(
        items=[ClientResponse.model_validate(c) for c in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{client_id}")
def get_client(client_id: UUID, clients: Clients, _: CurrentUser) -> ClientResponse:
    return ClientResponse.model_validate(GetClient(clients).execute(client_id))


@router.patch("/{client_id}")
def update_client(client_id: UUID, body: ClientUpdate, clients: Clients, _: CurrentUser) -> ClientResponse:
    data = UpdateClientInput(**body.model_dump(exclude_unset=True))
    return ClientResponse.model_validate(UpdateClient(clients).execute(client_id, data))
