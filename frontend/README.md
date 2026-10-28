# frontend

React + TypeScript (Vite) web app for the engine repair workshop. It signs in **only** against
`auth-service`, keeps the access token in `sessionStorage` (per tab) and sends it as a Bearer token to
`business-service`.

## Views

| Route | View |
|---|---|
| `/login` | Sign in (validated form, clear API errors, notice when the session expired) |
| `/` | Dashboard: orders per status (each card links to the filtered list) and recent orders |
| `/clients`, `/clients/:id` | List with search and pagination, create, detail, edit, activate/deactivate |
| `/engines`, `/engines/:id` | List with search and owner filter, create, detail with repair history, edit |
| `/orders` | List with search and filters by status, client and engine (kept in the URL) |
| `/orders/new` | Create an order; the client is derived from the selected engine |
| `/orders/:id` | Full detail, client approval, status update (only valid next states), history |
| `/users` | ADMIN only: create users, change role, activate/deactivate |

## Structure

```text
src/
├── api/          # fetch wrapper (Bearer token, problem+json errors), auth and business API clients, types
├── auth/         # AuthContext: login, profile (/auth/me), logout on 401 or token expiry
├── components/   # Layout, route guard, form fields, badges, alerts, spinner, pagination
├── lib/          # zod form schemas, labels and allowed transitions, data-loading hooks
├── pages/        # One component per view
└── __tests__/    # Vitest + Testing Library
```

The route guard and the hidden "Usuarios" link are only UX: every API enforces authentication and roles.

## Run

```bash
cd frontend
npm install
cp .env.example .env     # API base URLs
npm run dev              # http://localhost:5173
```

Checks: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`.
