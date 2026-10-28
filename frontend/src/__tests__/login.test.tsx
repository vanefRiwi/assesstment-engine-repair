import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { App } from "../App";
import { AuthProvider } from "../auth/AuthContext";

function jsonResponse(status: number, body: unknown) {
  return Promise.resolve(new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } }));
}

const fakeToken = `h.${btoa(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + 900 }))}.s`;

function renderApp() {
  return render(
    <MemoryRouter initialEntries={["/"]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("login flow", () => {
  beforeEach(() => sessionStorage.clear());
  afterEach(() => vi.restoreAllMocks());

  it("redirects to login and validates the form before calling the API", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    renderApp();

    await userEvent.click(await screen.findByRole("button", { name: "Iniciar sesión" }));
    expect(screen.getByText("Ingresa un correo válido")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("shows the API error for bad credentials", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(() =>
      jsonResponse(401, { status: 401, title: "Unauthorized", detail: "Invalid email or password." }),
    );
    renderApp();

    await userEvent.type(await screen.findByLabelText("Correo electrónico"), "op@example.com");
    await userEvent.type(screen.getByLabelText("Contraseña"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid email or password.");
  });

  it("signs in, sends the Bearer token to the business API and shows the dashboard", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.endsWith("/auth/login")) return jsonResponse(200, { access_token: fakeToken, token_type: "Bearer", expires_in: 900 });
      if (url.endsWith("/auth/me"))
        return jsonResponse(200, { id: "u1", name: "Ana", email: "op@example.com", role: "OPERATOR", is_active: true });
      if (url.includes("/repair-orders/summary"))
        return jsonResponse(200, { total: 3, by_status: { RECEIVED: 2, IN_REPAIR: 1 } });
      return jsonResponse(200, { items: [], total: 0, limit: 5, offset: 0 });
    });
    renderApp();

    await userEvent.type(await screen.findByLabelText("Correo electrónico"), "op@example.com");
    await userEvent.type(screen.getByLabelText("Contraseña"), "secret-123");
    await userEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(await screen.findByText("Órdenes totales")).toBeInTheDocument();
    expect(screen.getByText(/Ana · Operador/)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Usuarios" })).not.toBeInTheDocument();

    await waitFor(() => {
      const summaryCall = fetchMock.mock.calls.find(([url]) => String(url).includes("/repair-orders/summary"));
      const headers = new Headers((summaryCall?.[1] as RequestInit).headers);
      expect(headers.get("Authorization")).toBe(`Bearer ${fakeToken}`);
    });
  });
});
