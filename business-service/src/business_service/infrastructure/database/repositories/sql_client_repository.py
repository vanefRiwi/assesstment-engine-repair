from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, select

from business_service.domain.entities.client import Client
from business_service.domain.repositories.client_repository import ClientFilters, ClientRepository
from business_service.infrastructure.database.models.tables import ClientTable
from business_service.infrastructure.database.repositories.errors import translate_integrity_error


def _to_domain(row: ClientTable) -> Client:
    return Client(**row.model_dump())


class SqlClientRepository(ClientRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, client_id: UUID) -> Client | None:
        row = self.session.get(ClientTable, client_id)
        return _to_domain(row) if row else None

    def get_by_document(self, document_type: str, document_number: str) -> Client | None:
        statement = select(ClientTable).where(
            ClientTable.document_type == document_type, ClientTable.document_number == document_number
        )
        row = self.session.exec(statement).first()
        return _to_domain(row) if row else None

    def search(self, filters: ClientFilters) -> tuple[list[Client], int]:
        statement = select(ClientTable)
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            statement = statement.where(
                or_(ClientTable.name.ilike(pattern), ClientTable.document_number.ilike(pattern))  # type: ignore[union-attr]
            )
        if filters.is_active is not None:
            statement = statement.where(ClientTable.is_active == filters.is_active)

        total = self.session.exec(select(func.count()).select_from(statement.subquery())).one()
        rows = self.session.exec(statement.order_by(ClientTable.name).offset(filters.offset).limit(filters.limit)).all()
        return [_to_domain(row) for row in rows], total

    def add(self, client: Client) -> Client:
        self.session.add(ClientTable(**vars(client)))
        with translate_integrity_error():
            self.session.flush()
        return client

    def update(self, client: Client) -> Client:
        row = self.session.get(ClientTable, client.id)
        assert row is not None
        row.sqlmodel_update(vars(client))
        with translate_integrity_error():
            self.session.flush()
        return client
