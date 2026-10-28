from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from business_service.application.dto import CreateEngineInput, UpdateEngineInput
from business_service.application.use_cases.engines import CreateEngine, GetEngine, ListEngines, UpdateEngine
from business_service.domain.repositories.engine_repository import EngineFilters
from business_service.presentation.api.dependencies.auth import CurrentUser
from business_service.presentation.api.dependencies.repositories import Clients, Engines, Orders
from business_service.presentation.api.schemas.common import PageResponse
from business_service.presentation.api.schemas.engines import EngineCreate, EngineResponse, EngineUpdate

router = APIRouter(prefix="/engines", tags=["Engines"])


@router.post("", status_code=201)
def create_engine(
    body: EngineCreate, engines: Engines, clients: Clients, _: CurrentUser, response: Response
) -> EngineResponse:
    engine = CreateEngine(engines, clients).execute(CreateEngineInput(**body.model_dump()))
    response.headers["Location"] = f"/api/v1/engines/{engine.id}"
    return EngineResponse.model_validate(engine)


@router.get("")
def list_engines(
    engines: Engines,
    _: CurrentUser,
    q: Annotated[str | None, Query(max_length=100, description="Serial, manufacturer or model")] = None,
    client_id: UUID | None = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PageResponse[EngineResponse]:
    filters = EngineFilters(search=q, client_id=client_id, is_active=is_active, limit=limit, offset=offset)
    page = ListEngines(engines).execute(filters)
    return PageResponse(
        items=[EngineResponse.model_validate(e) for e in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{engine_id}")
def get_engine(engine_id: UUID, engines: Engines, _: CurrentUser) -> EngineResponse:
    return EngineResponse.model_validate(GetEngine(engines).execute(engine_id))


@router.patch("/{engine_id}")
def update_engine(
    engine_id: UUID, body: EngineUpdate, engines: Engines, clients: Clients, orders: Orders, _: CurrentUser
) -> EngineResponse:
    data = UpdateEngineInput(**body.model_dump(exclude_unset=True))
    return EngineResponse.model_validate(UpdateEngine(engines, clients, orders).execute(engine_id, data))
