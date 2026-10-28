"""End-to-end business flow through HTTP, with in-memory repositories."""

from uuid import uuid4


def create_client(client, headers, number="900123456"):
    body = {"name": "Mina Andina", "document_type": "NIT", "document_number": number, "email": "ops@mina.co"}
    return client.post("/api/v1/clients", json=body, headers=headers)


def create_engine(client, headers, client_id, serial="CAT-3516-001"):
    body = {
        "serial_number": serial,
        "manufacturer": "Caterpillar",
        "model": "3516B",
        "engine_type": "Diesel",
        "capacity": "2500 HP",
        "client_id": client_id,
    }
    return client.post("/api/v1/engines", json=body, headers=headers)


def create_order(client, headers, engine_id, **extra):
    body = {"engine_id": engine_id, "received_at": "2026-10-27T14:30:00Z", "reported_problem": "Loses power", **extra}
    return client.post("/api/v1/repair-orders", json=body, headers=headers)


def change_status(client, headers, order_id, status, **extra):
    return client.patch(f"/api/v1/repair-orders/{order_id}/status", json={"status": status, **extra}, headers=headers)


def test_clients_crud_and_duplicates(client, auth_headers):
    created = create_client(client, auth_headers)
    assert created.status_code == 201
    client_id = created.json()["id"]
    assert created.headers["location"] == f"/api/v1/clients/{client_id}"

    duplicate = create_client(client, auth_headers)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "A client with this document already exists."

    updated = client.patch(f"/api/v1/clients/{client_id}", json={"phone": "+57 300 000 0000"}, headers=auth_headers)
    assert updated.json()["phone"] == "+57 300 000 0000"

    listed = client.get("/api/v1/clients", params={"q": "andina"}, headers=auth_headers).json()
    assert listed["total"] == 1
    assert client.get(f"/api/v1/clients/{uuid4()}", headers=auth_headers).status_code == 404


def test_validation_errors_are_422_problems(client, auth_headers):
    response = client.post("/api/v1/clients", json={"name": "X", "id": "forced"}, headers=auth_headers)
    assert response.status_code == 422
    fields = {issue["field"] for issue in response.json()["errors"]}
    assert {"name", "document_type", "document_number", "id"} <= fields


def test_engines_duplicate_serial_and_filter_by_client(client, auth_headers):
    client_id = create_client(client, auth_headers).json()["id"]
    assert create_engine(client, auth_headers, client_id).status_code == 201
    assert create_engine(client, auth_headers, client_id).status_code == 409
    assert create_engine(client, auth_headers, str(uuid4()), serial="OTHER").status_code == 404

    listed = client.get("/api/v1/engines", params={"client_id": client_id}, headers=auth_headers).json()
    assert [e["serial_number"] for e in listed["items"]] == ["CAT-3516-001"]


def test_full_repair_lifecycle(client, auth_headers):
    client_id = create_client(client, auth_headers).json()["id"]
    engine_id = create_engine(client, auth_headers, client_id).json()["id"]

    order = create_order(client, auth_headers, engine_id).json()
    assert order["status"] == "RECEIVED"
    assert order["client_id"] == client_id
    assert order["order_number"].startswith("REP-")
    order_id = order["id"]

    assert change_status(client, auth_headers, order_id, "DELIVERED").status_code == 400
    change_status(client, auth_headers, order_id, "IN_DIAGNOSIS", technician_name="Laura Gómez")
    awaiting = change_status(
        client, auth_headers, order_id, "AWAITING_APPROVAL", technical_diagnosis="Worn turbocharger"
    ).json()
    assert awaiting["approval_status"] == "PENDING"

    blocked = change_status(client, auth_headers, order_id, "IN_REPAIR")
    assert blocked.status_code == 400

    approved = client.patch(
        f"/api/v1/repair-orders/{order_id}/approval",
        json={"decision": "APPROVED", "notes": "Approved by phone"},
        headers=auth_headers,
    ).json()
    assert approved["approval_status"] == "APPROVED"
    assert approved["approved_at"] is not None

    for status in ("IN_REPAIR", "IN_TESTING", "COMPLETED", "DELIVERED"):
        response = change_status(client, auth_headers, order_id, status)
        assert response.status_code == 200, response.json()
    assert response.json()["actual_delivery_at"] is not None

    history = client.get(f"/api/v1/repair-orders/{order_id}/history", headers=auth_headers).json()
    assert [h["status"] for h in history] == [
        "RECEIVED",
        "IN_DIAGNOSIS",
        "AWAITING_APPROVAL",
        "IN_REPAIR",
        "IN_TESTING",
        "COMPLETED",
        "DELIVERED",
    ]

    summary = client.get("/api/v1/repair-orders/summary", headers=auth_headers).json()
    assert summary["total"] == 1
    assert summary["by_status"]["DELIVERED"] == 1


def test_order_filters_and_ownership_rule(client, auth_headers):
    owner_id = create_client(client, auth_headers).json()["id"]
    other_id = create_client(client, auth_headers, number="800000001").json()["id"]
    engine_id = create_engine(client, auth_headers, owner_id).json()["id"]

    assert create_order(client, auth_headers, engine_id, client_id=other_id).status_code == 400
    first = create_order(client, auth_headers, engine_id).json()
    create_order(client, auth_headers, engine_id)
    change_status(client, auth_headers, first["id"], "IN_DIAGNOSIS")

    by_status = client.get("/api/v1/repair-orders", params={"status": "IN_DIAGNOSIS"}, headers=auth_headers).json()
    assert [o["id"] for o in by_status["items"]] == [first["id"]]
    by_client = client.get("/api/v1/repair-orders", params={"client_id": owner_id}, headers=auth_headers).json()
    assert by_client["total"] == 2
    assert client.get("/api/v1/repair-orders", params={"status": "BOGUS"}, headers=auth_headers).status_code == 422


def test_received_at_requires_timezone(client, auth_headers):
    client_id = create_client(client, auth_headers).json()["id"]
    engine_id = create_engine(client, auth_headers, client_id).json()["id"]
    response = create_order(client, auth_headers, engine_id, received_at="2026-10-27T14:30:00")
    assert response.status_code == 422
