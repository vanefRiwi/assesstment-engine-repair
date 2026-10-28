from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, select

from business_service.domain.entities.engine import Engine
from business_service.domain.repositories.engine_repository import EngineFilters, EngineRepository
from business_service.infrastructure.database.models.tables import EngineTable
from business_service.infrastructure.database.repositories.errors import translate_integrity_error


def _to_domain(row: EngineTable) -> Engine:
    return Engine(**row.model_dump())


class SqlEngineRepository(EngineRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, engine_id: UUID) -> Engine | None:
        row = self.session.get(EngineTable, engine_id)
        return _to_domain(row) if row else None

    def get_by_serial(self, serial_number: str) -> Engine | None:
        row = self.session.exec(select(EngineTable).where(EngineTable.serial_number == serial_number)).first()
        return _to_domain(row) if row else None

    def search(self, filters: EngineFilters) -> tuple[list[Engine], int]:
        statement = select(EngineTable)
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(
                    EngineTable.serial_number.ilike(pattern),  # type: ignore[union-attr]
                    EngineTable.manufacturer.ilike(pattern),  # type: ignore[union-attr]
                    EngineTable.model.ilike(pattern),  # type: ignore[union-attr]
                )
            )
        if filters.client_id:
            statement = statement.where(EngineTable.client_id == filters.client_id)
        if filters.is_active is not None:
            statement = statement.where(EngineTable.is_active == filters.is_active)

        total = self.session.exec(select(func.count()).select_from(statement.subquery())).one()
        rows = self.session.exec(
            statement.order_by(EngineTable.serial_number).offset(filters.offset).limit(filters.limit)
        ).all()
        return [_to_domain(row) for row in rows], total

    def add(self, engine: Engine) -> Engine:
        self.session.add(EngineTable(**vars(engine)))
        with translate_integrity_error():
            self.session.flush()
        return engine

    def update(self, engine: Engine) -> Engine:
        row = self.session.get(EngineTable, engine.id)
        assert row is not None
        row.sqlmodel_update(vars(engine))
        with translate_integrity_error():
            self.session.flush()
        return engine
