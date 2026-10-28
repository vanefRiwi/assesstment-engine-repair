from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from business_service.application.dto import ChangeStatusInput, CreateRepairOrderInput
from business_service.application.use_cases.repair_orders import (
    ChangeRepairOrderStatus,
    CreateRepairOrder,
    GetRepairOrder,
    GetRepairOrderHistory,
    GetRepairOrderSummary,
    ListRepairOrders,
    RecordApprovalDecision,
)
from business_service.domain.repositories.repair_order_repository import RepairOrderFilters
from business_service.domain.value_objects.statuses import RepairStatus
from business_service.presentation.api.dependencies.auth import CurrentUser
from business_service.presentation.api.dependencies.repositories import Clients, Engines, Orders
from business_service.presentation.api.schemas.common import PageResponse
from business_service.presentation.api.schemas.repair_orders import (
    ApprovalDecision,
    RepairOrderCreate,
    RepairOrderResponse,
    StatusChange,
    StatusHistoryResponse,
    StatusSummaryResponse,
)

router = APIRouter(prefix="/repair-orders", tags=["Repair orders"])


@router.post("", status_code=201)
def create_repair_order(
    body: RepairOrderCreate,
    orders: Orders,
    engines: Engines,
    clients: Clients,
    user: CurrentUser,
    response: Response,
) -> RepairOrderResponse:
    order = CreateRepairOrder(orders, engines, clients).execute(
        CreateRepairOrderInput(**body.model_dump()), created_by=user.user_id
    )
    response.headers["Location"] = f"/api/v1/repair-orders/{order.id}"
    return RepairOrderResponse.model_validate(order)


@router.get("")
def list_repair_orders(
    orders: Orders,
    _: CurrentUser,
    status: RepairStatus | None = None,
    client_id: UUID | None = None,
    engine_id: UUID | None = None,
    q: Annotated[str | None, Query(max_length=100, description="Order number, problem or technician")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PageResponse[RepairOrderResponse]:
    filters = RepairOrderFilters(
        status=status, client_id=client_id, engine_id=engine_id, search=q, limit=limit, offset=offset
    )
    page = ListRepairOrders(orders).execute(filters)
    return PageResponse(
        items=[RepairOrderResponse.model_validate(o) for o in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


# Declared before /{order_id} so "summary" is not parsed as an id.
@router.get("/summary")
def repair_order_summary(orders: Orders, _: CurrentUser) -> StatusSummaryResponse:
    counts = GetRepairOrderSummary(orders).execute()
    return StatusSummaryResponse(total=sum(counts.values()), by_status=counts)


@router.get("/{order_id}")
def get_repair_order(order_id: UUID, orders: Orders, _: CurrentUser) -> RepairOrderResponse:
    return RepairOrderResponse.model_validate(GetRepairOrder(orders).execute(order_id))


@router.patch("/{order_id}/status")
def change_repair_order_status(
    order_id: UUID, body: StatusChange, orders: Orders, user: CurrentUser
) -> RepairOrderResponse:
    data = ChangeStatusInput(**body.model_dump())
    order = ChangeRepairOrderStatus(orders).execute(order_id, data, changed_by=user.user_id)
    return RepairOrderResponse.model_validate(order)


@router.patch("/{order_id}/approval")
def record_approval(order_id: UUID, body: ApprovalDecision, orders: Orders, _: CurrentUser) -> RepairOrderResponse:
    order = RecordApprovalDecision(orders).execute(order_id, body.decision, body.notes)
    return RepairOrderResponse.model_validate(order)


@router.get("/{order_id}/history")
def repair_order_history(order_id: UUID, orders: Orders, _: CurrentUser) -> list[StatusHistoryResponse]:
    return [StatusHistoryResponse.model_validate(e) for e in GetRepairOrderHistory(orders).execute(order_id)]
