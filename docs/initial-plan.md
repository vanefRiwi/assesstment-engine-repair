# Initial Technical Planning

## 1. Business workflow

The first end-to-end acceptance scenario is:

1. An authorized user signs in through the authentication API.
2. The frontend receives a signed JWT.
3. The user registers a client.
4. The user registers an engine linked to that client.
5. The user creates a repair order for the engine.
6. The user views the order details and its status history.
7. The business API rejects requests without a valid JWT.

## 2. Domain entities

- **User** (auth service): identity, email, password hash, role, active flag.
- **Client** (business service): legal/name, document type and number, email, active flag.
- **Engine** (business service): unique serial number, manufacturer, model, type, capacity, client reference, registration date, active flag.
- **RepairOrder** (business service): order number, engine and client references, received date, reported problem, diagnosis, work required/performed, technician reference, estimated and actual delivery dates, current status, notes, created/updated timestamps.
- **RepairStatusHistory** (business service): repair order reference, status, timestamp, optional note.

## 3. Initial relationships and integrity rules

- One client can own multiple engines.
- One engine can have multiple repair orders over time.
- Each repair order refers to an existing engine and its owning client.
- Client document type + number must be unique.
- Engine serial number must be unique.
- Repair order status changes should create history records.
- Status history should be appended rather than overwritten.

## 4. Architecture decisions to make before feature coding

- Use a monorepo with independently runnable services and frontend.
- Keep authentication data owned by the auth service and operational data owned by the business service.
- A single local PostgreSQL server with separate databases and service-specific credentials is a reasonable simple setup; do not let one service query the other's internal tables.
- Configure the JWT algorithm explicitly and validate signature, expiry, issuer/audience if configured, and required claims in FastAPI.
- Clarify whether client/engine editing is in scope: the specification is inconsistent between sections. Prioritize create/list/detail and repair-status tracking first.

## 5. First implementation milestones

- [ ] Confirm local tools and versions: Git, Node.js/npm, Python, Docker.
- [ ] Draw architecture diagram and ER diagram.
- [ ] Define API endpoint contracts and common error formats.
- [ ] Initialize the three projects.
- [ ] Add database migrations and health checks.
- [ ] Implement auth API and tests.
- [ ] Implement business API and tests.
- [ ] Integrate frontend and end-to-end flow.
- [ ] Add Compose, GitHub Actions, and final documentation.
