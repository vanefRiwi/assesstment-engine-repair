"""In-memory repositories: use cases and routes are tested without a database."""

from dataclasses import replace
from uuid import UUID

from business_service.domain.entities.client import Client
from business_service.domain.entities.engine import Engine
from business_service.domain.entities.repair_order import RepairOrder, StatusHistoryEntry
from business_service.domain.repositories.client_repository import ClientFilters, ClientRepository
from business_service.domain.repositories.engine_repository import EngineFilters, EngineRepository
from business_service.domain.repositories.repair_order_repository import (
    RepairOrderFilters,
    RepairOrderRepository,
)
from business_service.domain.value_objects.statuses import RepairStatus


def _page(items: list, limit: int, offset: int) -> tuple[list, int]:
    return items[offset : offset + limit], len(items)


class InMemoryClientRepository(ClientRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Client] = {}

    def get(self, client_id):
        item = self.items.get(client_id)
        return replace(item) if item else None

    def get_by_document(self, document_type, document_number):
        return next(
            (
                c
                for c in self.items.values()
                if (c.document_type, c.document_number) == (document_type, document_number)
            ),
            None,
        )

    def search(self, filters: ClientFilters):
        items = sorted(self.items.values(), key=lambda c: c.name)
        if filters.search:
            term = filters.search.lower()
            items = [c for c in items if term in c.name.lower() or term in c.document_number.lower()]
        if filters.is_active is not None:
            items = [c for c in items if c.is_active == filters.is_active]
        return _page(items, filters.limit, filters.offset)

    def add(self, client):
        self.items[client.id] = replace(client)
        return client

    def update(self, client):
        self.items[client.id] = replace(client)
        return client


class InMemoryEngineRepository(EngineRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Engine] = {}

    def get(self, engine_id):
        item = self.items.get(engine_id)
        return replace(item) if item else None

    def get_by_serial(self, serial_number):
        return next((e for e in self.items.values() if e.serial_number == serial_number), None)

    def search(self, filters: EngineFilters):
        items = sorted(self.items.values(), key=lambda e: e.serial_number)
        if filters.search:
            term = filters.search.lower()
            items = [e for e in items if term in f"{e.serial_number} {e.manufacturer} {e.model}".lower()]
        if filters.client_id:
            items = [e for e in items if e.client_id == filters.client_id]
        if filters.is_active is not None:
            items = [e for e in items if e.is_active == filters.is_active]
        return _page(items, filters.limit, filters.offset)

    def add(self, engine):
        self.items[engine.id] = replace(engine)
        return engine

    def update(self, engine):
        self.items[engine.id] = replace(engine)
        return engine


class InMemoryRepairOrderRepository(RepairOrderRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, RepairOrder] = {}
        self.history_entries: list[StatusHistoryEntry] = []
        self._sequence = 0

    def next_order_number(self):
        self._sequence += 1
        return f"REP-2026-{self._sequence:06d}"

    def get(self, order_id):
        item = self.items.get(order_id)
        return replace(item) if item else None

    def search(self, filters: RepairOrderFilters):
        items = sorted(self.items.values(), key=lambda o: o.created_at, reverse=True)
        if filters.status:
            items = [o for o in items if o.status == filters.status]
        if filters.client_id:
            items = [o for o in items if o.client_id == filters.client_id]
        if filters.engine_id:
            items = [o for o in items if o.engine_id == filters.engine_id]
        if filters.search:
            term = filters.search.lower()
            items = [o for o in items if term in f"{o.order_number} {o.reported_problem}".lower()]
        return _page(items, filters.limit, filters.offset)

    def add(self, order, history):
        self.items[order.id] = replace(order)
        self.history_entries.append(history)
        return order

    def update(self, order, history=None):
        self.items[order.id] = replace(order)
        if history:
            self.history_entries.append(history)
        return order

    def history(self, order_id):
        return [h for h in self.history_entries if h.repair_order_id == order_id]

    def count_by_status(self):
        counts: dict[RepairStatus, int] = {}
        for order in self.items.values():
            counts[order.status] = counts.get(order.status, 0) + 1
        return counts

    def exists_for_engine(self, engine_id):
        return any(o.engine_id == engine_id for o in self.items.values())
