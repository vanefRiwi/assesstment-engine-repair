# business-service

Business API (FastAPI + Python) for clients, engines and repair orders. It owns the business database,
never stores passwords and has no login: every endpoint except `/health` requires an RS256 access token
issued by `auth-service`, verified here with the public key only.

## Clean Architecture layout

```text
src/business_service/
├── domain/              # Entities (Client, Engine, RepairOrder), statuses, transition rules, repository contracts
├── application/         # Use cases (one class per action) and input DTOs
├── infrastructure/      # Settings, SQLModel tables, SQL repositories, DB session, JWT verifier
├── presentation/api/    # FastAPI routes, Pydantic schemas, dependencies, problem+json error handlers
└── main.py              # App factory
alembic/                 # Versioned migrations (the schema is never created with create_all)
tests/
├── unit/                # Domain rules and use cases with in-memory repositories
├── api/                 # HTTP tests: business flow and JWT rejection cases
└── integration/         # Same flow against PostgreSQL + Alembic (needs TEST_DATABASE_URL)
```

Dependencies point inward. The domain does not import FastAPI, SQLModel or PostgreSQL. Routes only
translate HTTP to use cases, and `presentation/api/dependencies/repositories.py` is the single place that
chooses the SQL repositories (tests swap in in-memory fakes there).

## Business rules

- Unique client document (`document_type` + `document_number`, normalized) and engine serial number → `409`.
- A repair order's client is the engine's owner; a mismatching `client_id` → `400`, and a composite
  foreign key enforces it in the database too.
- Inactive clients cannot receive engines; inactive engines or clients cannot get new orders.
- An engine's owner cannot change once it has repair orders (history stays correct).
- Order numbers `REP-<year>-<000001>` come from a PostgreSQL sequence, safe under concurrency.
- Status flow: `RECEIVED → IN_DIAGNOSIS → AWAITING_APPROVAL → IN_REPAIR → IN_TESTING → COMPLETED → DELIVERED`,
  plus `IN_TESTING → IN_REPAIR` (failed test) and `AWAITING_APPROVAL → IN_DIAGNOSIS` (revise proposal).
- Entering `AWAITING_APPROVAL` sets approval to `PENDING`; `IN_REPAIR` requires `APPROVED`.
- Entering `DELIVERED` sets `actual_delivery_at`.
- Every status change appends a history row (with the user id from the token) in the same transaction.

## Endpoints

Swagger UI: `http://localhost:8000/api/v1/docs`. All under `/api/v1`, roles `ADMIN` and `OPERATOR`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Public liveness check |
| POST / GET | `/clients` | Create / list (`q`, `is_active`, `limit`, `offset`) |
| GET / PATCH | `/clients/{id}` | Detail / edit (name, email, phone, `is_active`) |
| POST / GET | `/engines` | Create / list (`q`, `client_id`, `is_active`, pagination) |
| GET / PATCH | `/engines/{id}` | Detail / edit |
| POST / GET | `/repair-orders` | Create / list (`status`, `client_id`, `engine_id`, `q`, pagination) |
| GET | `/repair-orders/summary` | Count per status for the dashboard |
| GET | `/repair-orders/{id}` | Detail |
| PATCH | `/repair-orders/{id}/status` | Transition, optionally filling diagnosis, work, technician, estimated date |
| PATCH | `/repair-orders/{id}/approval` | Record `APPROVED` / `REJECTED` while awaiting approval |
| GET | `/repair-orders/{id}/history` | Chronological status history |

## JWT verification

`JwtVerifier` uses PyJWT with an explicit `RS256` allow-list and checks signature, `exp`, `iss`, `aud`,
the presence of `sub`, `iat`, `exp`, `jti`, that `sub` is a UUID and that `role` is `ADMIN` or `OPERATOR`.
Any failure returns `401` with `WWW-Authenticate: Bearer`. Unsigned (`alg: none`) tokens, foreign keys,
expired tokens and wrong issuer/audience are covered by tests.

## Local setup

```bash
cd business-service
uv sync
cp .env.example .env                        # point JWT_PUBLIC_KEY_PATH to auth-service/secrets/jwt-public.pem
uv run alembic upgrade head
uv run uvicorn business_service.main:app --reload --port 8000
```

## Checks

```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest                                # unit + API tests
TEST_DATABASE_URL=postgresql://... uv run pytest   # also runs the PostgreSQL integration test
```
