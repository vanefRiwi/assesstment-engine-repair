# Motor Repair Management Platform

Full-stack technical assessment: a platform to manage heavy mining engine repairs.

## Project status

Initial planning stage. The repository structure and technical decisions will be established before implementing application features.

## Required stack

- **Authentication and users API:** Node.js, Express, TypeScript
- **Business API:** Python, FastAPI
- **Frontend:** React, TypeScript
- **Persistence:** PostgreSQL
- **Local orchestration:** Docker Compose
- **CI:** GitHub Actions

## Architecture overview

- `auth-service/` owns user registration, login, password hashing, roles, and JWT issuance.
- `business-service/` owns clients, engines, repair orders, repair status history, and validation of JWTs issued by the auth service.
- `frontend/` provides the web interface and consumes both APIs. Authentication is performed exclusively through the auth API.
- Each backend service must have its own persistence responsibility; neither service should access the other service's internal tables.

## Planned repository layout

```text
.
├── auth-service/
├── business-service/
├── frontend/
├── database/
│   └── migrations/
├── docs/
├── .github/
│   └── workflows/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Initial implementation plan

1. Document the architecture, domain entities, relationships, and API contracts.
2. Initialize the Express/TypeScript, FastAPI, and React/TypeScript projects.
3. Implement authentication and JWT issuance in the auth service.
4. Implement clients, engines, repair orders, status history, and JWT verification in the business service.
5. Integrate the frontend with both APIs.
6. Add automated tests, Docker Compose, and GitHub Actions CI.
7. Complete setup instructions and technical documentation.

## Security notes

- Never commit real credentials, JWT signing keys, tokens, or production secrets.
- Keep `.env` files out of version control and maintain `.env.example` with placeholder values only.
- The business API must validate JWT signature, expiry, and required claims; decoding alone is not sufficient.

## Status

Planning and repository scaffolding.