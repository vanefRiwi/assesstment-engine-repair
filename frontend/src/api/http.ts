/** Small fetch wrapper: adds the Bearer token, parses problem+json errors, and reports expired sessions. */

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly fieldErrors: { field: string; message: string }[] = [],
  ) {
    super(message);
  }
}

let accessToken: string | null = null;
let onUnauthorized: () => void = () => {};

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler;
}

export async function request<T>(baseUrl: string, path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, "No se pudo conectar con el servidor. Verifica que los servicios estén activos.");
  }

  if (response.status === 401 && accessToken) onUnauthorized();
  if (!response.ok) {
    const problem = await response.json().catch(() => ({}));
    throw new ApiError(response.status, problem.detail ?? `Error ${response.status}`, problem.errors ?? []);
  }
  return (await response.json()) as T;
}

export function toQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}
