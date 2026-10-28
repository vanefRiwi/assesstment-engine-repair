from dataclasses import replace
from uuid import UUID

from business_service.application.dto import CreateEngineInput, Page, UpdateEngineInput
from business_service.application.use_cases.clients import get_client_or_fail
from business_service.domain.entities.engine import Engine
from business_service.domain.exceptions import BusinessRuleError, ConflictError, NotFoundError
from business_service.domain.repositories.client_repository import ClientRepository
from business_service.domain.repositories.engine_repository import EngineFilters, EngineRepository
from business_service.domain.repositories.repair_order_repository import RepairOrderRepository
from business_service.domain.time import utc_now


def get_engine_or_fail(engines: EngineRepository, engine_id: UUID) -> Engine:
    engine = engines.get(engine_id)
    if engine is None:
        raise NotFoundError("Engine not found.")
    return engine


class CreateEngine:
    def __init__(self, engines: EngineRepository, clients: ClientRepository) -> None:
        self.engines = engines
        self.clients = clients

    def execute(self, data: CreateEngineInput) -> Engine:
        owner = get_client_or_fail(self.clients, data.client_id)
        if not owner.is_active:
            raise BusinessRuleError("Engines cannot be registered for an inactive client.")

        engine = Engine(
            serial_number=data.serial_number,
            manufacturer=data.manufacturer,
            model=data.model,
            engine_type=data.engine_type,
            capacity=data.capacity,
            client_id=data.client_id,
        )
        if self.engines.get_by_serial(engine.serial_number):
            raise ConflictError("An engine with this serial number already exists.")
        return self.engines.add(engine)


class UpdateEngine:
    def __init__(self, engines: EngineRepository, clients: ClientRepository, orders: RepairOrderRepository) -> None:
        self.engines = engines
        self.clients = clients
        self.orders = orders

    def execute(self, engine_id: UUID, data: UpdateEngineInput) -> Engine:
        engine = get_engine_or_fail(self.engines, engine_id)
        changes = {key: value for key, value in vars(data).items() if value is not None}

        if "client_id" in changes and changes["client_id"] != engine.client_id:
            owner = get_client_or_fail(self.clients, changes["client_id"])
            if not owner.is_active:
                raise BusinessRuleError("An engine cannot be assigned to an inactive client.")
            # Orders keep the owner they were created with; rewriting them would corrupt history.
            if self.orders.exists_for_engine(engine_id):
                raise ConflictError("The owner of an engine with repair orders cannot be changed.")

        if not changes:
            return engine
        return self.engines.update(replace(engine, **changes, updated_at=utc_now()))


class GetEngine:
    def __init__(self, engines: EngineRepository) -> None:
        self.engines = engines

    def execute(self, engine_id: UUID) -> Engine:
        return get_engine_or_fail(self.engines, engine_id)


class ListEngines:
    def __init__(self, engines: EngineRepository) -> None:
        self.engines = engines

    def execute(self, filters: EngineFilters) -> Page[Engine]:
        items, total = self.engines.search(filters)
        return Page(items=items, total=total, limit=filters.limit, offset=filters.offset)
