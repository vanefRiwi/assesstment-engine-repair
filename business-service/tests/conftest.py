import pytest
from fastapi.testclient import TestClient

from business_service.infrastructure.security.jwt_verifier import JwtVerifier
from business_service.main import create_app
from business_service.presentation.api.dependencies.auth import get_jwt_verifier
from business_service.presentation.api.dependencies.repositories import (
    get_client_repository,
    get_engine_repository,
    get_repair_order_repository,
)
from tests.fakes import InMemoryClientRepository, InMemoryEngineRepository, InMemoryRepairOrderRepository
from tests.tokens import AUDIENCE, ISSUER, PUBLIC_KEY, make_token


@pytest.fixture
def verifier() -> JwtVerifier:
    return JwtVerifier(PUBLIC_KEY, ISSUER, AUDIENCE)


@pytest.fixture
def repos():
    return InMemoryClientRepository(), InMemoryEngineRepository(), InMemoryRepairOrderRepository()


@pytest.fixture
def client(repos, verifier) -> TestClient:
    clients, engines, orders = repos
    app = create_app()
    app.dependency_overrides[get_jwt_verifier] = lambda: verifier
    app.dependency_overrides[get_client_repository] = lambda: clients
    app.dependency_overrides[get_engine_repository] = lambda: engines
    app.dependency_overrides[get_repair_order_repository] = lambda: orders
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token()}"}
