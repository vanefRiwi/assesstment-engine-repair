from uuid import UUID

from business_service.application.dto import ChangeStatusInput, CreateRepairOrderInput, Page
from business_service.application.use_cases.clients import get_client_or_fail
from business_service.application.use_cases.engines import get_engine_or_fail
from business_service.domain.entities.repair_order import RepairOrder, StatusHistoryEntry
from business_service.domain.exceptions import BusinessRuleError, NotFoundError
from business_service.domain.repositories.client_repository import ClientRepository
from business_service.domain.repositories.engine_repository import EngineRepository
from business_service.domain.repositories.repair_order_repository import (
    RepairOrderFilters,
    RepairOrderRepository,
)
from business_service.domain.value_objects.statuses import ApprovalStatus, RepairStatus


def get_order_or_fail(orders: RepairOrderRepository, order_id: UUID) -> RepairOrder:
    order = orders.get(order_id)
    if order is None:
        raise NotFoundError("Repair order not found.")
    return order


class CreateRepairOrder:
    def __init__(self, orders: RepairOrderRepository, engines: EngineRepository, clients: ClientRepository) -> None:
        self.orders = orders
        self.engines = engines
        self.clients = clients

    def execute(self, data: CreateRepairOrderInput, created_by: UUID) -> RepairOrder:
        engine = get_engine_or_fail(self.engines, data.engine_id)
        if not engine.is_active:
            raise BusinessRuleError("Repair orders cannot be created for an inactive engine.")

        # The client is the engine's owner; an explicit client_id must agree with it.
        if data.client_id is not None and data.client_id != engine.client_id:
            raise BusinessRuleError("The client must be the current owner of the engine.")
        client = get_client_or_fail(self.clients, engine.client_id)
        if not client.is_active:
            raise BusinessRuleError("Repair orders cannot be created for an inactive client.")

        order = RepairOrder(
            order_number=self.orders.next_order_number(),
            engine_id=engine.id,
            client_id=client.id,
            received_at=data.received_at,
            reported_problem=data.reported_problem,
            technical_diagnosis=data.technical_diagnosis,
            repair_description=data.repair_description,
            technician_name=data.technician_name,
            estimated_delivery_at=data.estimated_delivery_at,
            observations=data.observations,
        )
        return self.orders.add(order, order.initial_history(created_by))


class GetRepairOrder:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self, order_id: UUID) -> RepairOrder:
        return get_order_or_fail(self.orders, order_id)


class ListRepairOrders:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self, filters: RepairOrderFilters) -> Page[RepairOrder]:
        items, total = self.orders.search(filters)
        return Page(items=items, total=total, limit=filters.limit, offset=filters.offset)


class ChangeRepairOrderStatus:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self, order_id: UUID, data: ChangeStatusInput, changed_by: UUID) -> RepairOrder:
        order = get_order_or_fail(self.orders, order_id)
        order.update_technical_details(
            technical_diagnosis=data.technical_diagnosis,
            repair_description=data.repair_description,
            technician_name=data.technician_name,
            estimated_delivery_at=data.estimated_delivery_at,
        )
        history = order.change_status(RepairStatus(data.status), changed_by, data.observations)
        # The repository persists the order and its history row in the same transaction.
        return self.orders.update(order, history)


class RecordApprovalDecision:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self, order_id: UUID, decision: str, notes: str | None) -> RepairOrder:
        order = get_order_or_fail(self.orders, order_id)
        order.record_approval(ApprovalStatus(decision), notes)
        return self.orders.update(order)


class GetRepairOrderHistory:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self, order_id: UUID) -> list[StatusHistoryEntry]:
        get_order_or_fail(self.orders, order_id)
        return self.orders.history(order_id)


class GetRepairOrderSummary:
    def __init__(self, orders: RepairOrderRepository) -> None:
        self.orders = orders

    def execute(self) -> dict[RepairStatus, int]:
        counts = self.orders.count_by_status()
        return {status: counts.get(status, 0) for status in RepairStatus}
