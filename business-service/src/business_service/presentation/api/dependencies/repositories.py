"""Composition root for persistence: the only place that picks the concrete repositories."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from business_service.domain.repositories.client_repository import ClientRepository
from business_service.domain.repositories.engine_repository import EngineRepository
from business_service.domain.repositories.repair_order_repository import RepairOrderRepository
from business_service.infrastructure.database.repositories.sql_client_repository import SqlClientRepository
from business_service.infrastructure.database.repositories.sql_engine_repository import SqlEngineRepository
from business_service.infrastructure.database.repositories.sql_repair_order_repository import (
    SqlRepairOrderRepository,
)
from business_service.infrastructure.database.session import get_session

# scope="function" commits before the response is sent, so clients never see uncommitted data.
SessionDep = Annotated[Session, Depends(get_session, scope="function")]


def get_client_repository(session: SessionDep) -> ClientRepository:
    return SqlClientRepository(session)


def get_engine_repository(session: SessionDep) -> EngineRepository:
    return SqlEngineRepository(session)


def get_repair_order_repository(session: SessionDep) -> RepairOrderRepository:
    return SqlRepairOrderRepository(session)


Clients = Annotated[ClientRepository, Depends(get_client_repository)]
Engines = Annotated[EngineRepository, Depends(get_engine_repository)]
Orders = Annotated[RepairOrderRepository, Depends(get_repair_order_repository)]
