import { request } from "./http";
import type { Role, User } from "./types";

const AUTH_URL = import.meta.env.VITE_AUTH_API_URL ?? "http://localhost:3001/api/v1";

export interface TokenResponse {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
}

export const authApi = {
  login: (email: string, password: string) =>
    request<TokenResponse>(AUTH_URL, "/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request<User>(AUTH_URL, "/auth/me"),
  listUsers: () => request<User[]>(AUTH_URL, "/users"),
  createUser: (body: { name: string; email: string; password: string; role: Role }) =>
    request<User>(AUTH_URL, "/users", { method: "POST", body: JSON.stringify(body) }),
  updateUser: (id: string, body: { name?: string; role?: Role }) =>
    request<User>(AUTH_URL, `/users/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  setUserStatus: (id: string, isActive: boolean) =>
    request<User>(AUTH_URL, `/users/${id}/status`, { method: "PATCH", body: JSON.stringify({ is_active: isActive }) }),
};
