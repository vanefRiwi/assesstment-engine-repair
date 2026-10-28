from datetime import UTC, datetime
from uuid import uuid4

import pytest

from business_service.application.dto import (
    ChangeStatusInput,
    CreateClientInput,
    CreateEngineInput,
    CreateRepairOrderInput,
    UpdateClientInput,
    UpdateEngineInput,
)
from business_service.application.use_cases.clients import CreateClient, UpdateClient
from business_service.application.use_cases.engines import CreateEngine, UpdateEngine
from business_service.application.use_cases.repair_orders import (
    ChangeRepairOrderStatus,
    CreateRepairOrder,
    GetRepairOrderHistory,
    GetRepairOrderSummary,
)
from business_service.domain.exceptions import BusinessRuleError, ConflictError, NotFoundError
from business_service.domain.value_objects.statuses import RepairStatus
from tests.fakes import InMemoryClientRepository, InMemoryEngineRepository, InMemoryRepairOrderRepository

USER = uuid4()


@pytest.fixture
def clients():
    return InMemoryClientRepository()


@pytest.fixture
def engines():
    return InMemoryEngineRepository()


@pytest.fixture
def orders():
    return InMemoryRepairOrderRepository()


def make_client(clients, number="900123456"):
    return CreateClient(clients).execute(CreateClientInput("Mina Andina", "nit", number, "OPS@MINA.CO"))


def make_engine(engines, clients, client_id, serial="cat-3516"):
    return CreateEngine(engines, clients).execute(CreateEngineInput(serial, "Caterpillar", "3516", "Diesel", client_id))


def make_order(orders, engines, clients, engine_id, client_id=None):
    data = CreateRepairOrderInput(engine_id, datetime.now(UTC), "Loses power", client_id=client_id)
    return CreateRepairOrder(orders, engines, clients).execute(data, created_by=USER)


def test_client_identifiers_are_normalized_and_unique(clients):
    client = make_client(clients)
    assert (client.document_type, client.email) == ("NIT", "ops@mina.co")
    with pytest.raises(ConflictError):
        CreateClient(clients).execute(CreateClientInput("Other", " NIT ", "900 123 456"))


def test_engine_serial_is_unique_and_owner_must_exist(clients, engines):
    owner = make_client(clients)
    make_engine(engines, clients, owner.id)
    with pytest.raises(ConflictError):
        make_engine(engines, clients, owner.id, serial=" CAT-3516 ")
    with pytest.raises(NotFoundError):
        make_engine(engines, clients, uuid4(), serial="other")


def test_inactive_client_cannot_receive_engines(clients, engines):
    owner = make_client(clients)
    UpdateClient(clients).execute(owner.id, UpdateClientInput(is_active=False))
    with pytest.raises(BusinessRuleError):
        make_engine(engines, clients, owner.id)


def test_order_takes_client_from_engine_and_records_history(clients, engines, orders):
    owner = make_client(clients)
    engine = make_engine(engines, clients, owner.id)
    order = make_order(orders, engines, clients, engine.id)

    assert order.client_id == owner.id
    assert order.order_number == "REP-2026-000001"
    history = GetRepairOrderHistory(orders).execute(order.id)
    assert [(h.status, h.changed_by) for h in history] == [(RepairStatus.RECEIVED, USER)]


def test_order_rejects_client_that_does_not_own_engine(clients, engines, orders):
    owner = make_client(clients)
    other = make_client(clients, number="111")
    engine = make_engine(engines, clients, owner.id)
    with pytest.raises(BusinessRuleError):
        make_order(orders, engines, clients, engine.id, client_id=other.id)


def test_inactive_engine_cannot_get_orders(clients, engines, orders):
    owner = make_client(clients)
    engine = make_engine(engines, clients, owner.id)
    UpdateEngine(engines, clients, orders).execute(engine.id, UpdateEngineInput(is_active=False))
    with pytest.raises(BusinessRuleError):
        make_order(orders, engines, clients, engine.id)


def test_engine_owner_is_locked_once_it_has_orders(clients, engines, orders):
    owner = make_client(clients)
    other = make_client(clients, number="222")
    engine = make_engine(engines, clients, owner.id)
    make_order(orders, engines, clients, engine.id)
    with pytest.raises(ConflictError):
        UpdateEngine(engines, clients, orders).execute(engine.id, UpdateEngineInput(client_id=other.id))


def test_status_change_appends_history_and_updates_details(clients, engines, orders):
    owner = make_client(clients)
    engine = make_engine(engines, clients, owner.id)
    order = make_order(orders, engines, clients, engine.id)

    updated = ChangeRepairOrderStatus(orders).execute(
        order.id,
        ChangeStatusInput(status="IN_DIAGNOSIS", observations="Started", technician_name="Laura Gómez"),
        changed_by=USER,
    )
    assert updated.technician_name == "Laura Gómez"
    assert [h.status for h in orders.history(order.id)] == [RepairStatus.RECEIVED, RepairStatus.IN_DIAGNOSIS]
    assert GetRepairOrderSummary(orders).execute()[RepairStatus.IN_DIAGNOSIS] == 1
