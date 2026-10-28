"""Runs the HTTP flow against a real PostgreSQL schema created by Alembic.

Skipped unless TEST_DATABASE_URL points to a disposable database (CI provides one).
"""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = [pytest.mark.postgres, pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL not set")]


@pytest.fixture(scope="module")
def pg_client(verifier_module):
    from alembic.config import Config

    from alembic import command
    from business_service.infrastructure.config.settings import get_settings
    from business_service.infrastructure.database.session import get_engine

    os.environ["BUSINESS_DATABASE_URL"] = DATABASE_URL
    get_settings.cache_clear()
    get_engine.cache_clear()

    alembic_config = Config(os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini"))
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    from business_service.main import create_app
    from business_service.presentation.api.dependencies.auth import get_jwt_verifier

    app = create_app()
    app.dependency_overrides[get_jwt_verifier] = lambda: verifier_module
    yield TestClient(app)
    get_engine().dispose()


@pytest.fixture(scope="module")
def verifier_module():
    from business_service.infrastructure.security.jwt_verifier import JwtVerifier
    from tests.tokens import AUDIENCE, ISSUER, PUBLIC_KEY

    return JwtVerifier(PUBLIC_KEY, ISSUER, AUDIENCE)


@pytest.fixture
def headers():
    from tests.tokens import make_token

    return {"Authorization": f"Bearer {make_token()}"}


def test_lifecycle_persists_in_postgres(pg_client, headers):
    suffix = uuid4().hex[:8]
    client_id = pg_client.post(
        "/api/v1/clients",
        json={"name": "Minera PG", "document_type": "NIT", "document_number": f"PG{suffix}"},
        headers=headers,
    ).json()["id"]

    duplicate = pg_client.post(
        "/api/v1/clients",
        json={"name": "Dup", "document_type": "nit", "document_number": f"pg{suffix}"},
        headers=headers,
    )
    assert duplicate.status_code == 409

    engine_id = pg_client.post(
        "/api/v1/engines",
        json={
            "serial_number": f"SN-{suffix}",
            "manufacturer": "Cummins",
            "model": "QSK60",
            "engine_type": "Diesel",
            "client_id": client_id,
        },
        headers=headers,
    ).json()["id"]

    first = pg_client.post(
        "/api/v1/repair-orders",
        json={"engine_id": engine_id, "received_at": "2026-10-27T14:30:00Z", "reported_problem": "Overheats"},
        headers=headers,
    ).json()
    second = pg_client.post(
        "/api/v1/repair-orders",
        json={"engine_id": engine_id, "received_at": "2026-10-27T15:30:00Z", "reported_problem": "Noise"},
        headers=headers,
    ).json()
    assert first["order_number"] != second["order_number"]

    order_id = first["id"]
    for status in ("IN_DIAGNOSIS", "AWAITING_APPROVAL"):
        assert (
            pg_client.patch(
                f"/api/v1/repair-orders/{order_id}/status", json={"status": status}, headers=headers
            ).status_code
            == 200
        )
    pg_client.patch(f"/api/v1/repair-orders/{order_id}/approval", json={"decision": "APPROVED"}, headers=headers)
    assert (
        pg_client.patch(
            f"/api/v1/repair-orders/{order_id}/status", json={"status": "IN_REPAIR"}, headers=headers
        ).status_code
        == 200
    )

    history = pg_client.get(f"/api/v1/repair-orders/{order_id}/history", headers=headers).json()
    assert [h["status"] for h in history] == ["RECEIVED", "IN_DIAGNOSIS", "AWAITING_APPROVAL", "IN_REPAIR"]

    filtered = pg_client.get(
        "/api/v1/repair-orders", params={"engine_id": engine_id, "q": "overheat"}, headers=headers
    ).json()
    assert [o["id"] for o in filtered["items"]] == [order_id]

    summary = pg_client.get("/api/v1/repair-orders/summary", headers=headers).json()
    assert summary["by_status"]["IN_REPAIR"] >= 1

    other_client = pg_client.post(
        "/api/v1/clients",
        json={"name": "Other", "document_type": "NIT", "document_number": f"OT{suffix}"},
        headers=headers,
    ).json()["id"]
    locked = pg_client.patch(f"/api/v1/engines/{engine_id}", json={"client_id": other_client}, headers=headers)
    assert locked.status_code == 409
