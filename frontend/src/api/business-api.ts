import { request, toQuery } from "./http";
import type {
  Client,
  Engine,
  Page,
  RepairOrder,
  RepairStatus,
  StatusHistoryEntry,
  StatusSummary,
} from "./types";

const BUSINESS_URL = import.meta.env.VITE_BUSINESS_API_URL ?? "http://localhost:8000/api/v1";

type Query = Record<string, string | number | boolean | undefined>;
const get = <T,>(path: string) => request<T>(BUSINESS_URL, path);
const send = <T,>(method: "POST" | "PATCH", path: string, body: unknown) =>
  request<T>(BUSINESS_URL, path, { method, body: JSON.stringify(body) });

export type ClientInput = Pick<Client, "name" | "document_type" | "document_number"> & {
  email?: string;
  phone?: string;
};
export type EngineInput = Pick<Engine, "serial_number" | "manufacturer" | "model" | "engine_type" | "client_id"> & {
  capacity?: string;
};
export interface RepairOrderInput {
  engine_id: string;
  received_at: string;
  reported_problem: string;
  technician_name?: string;
  estimated_delivery_at?: string;
  observations?: string;
}
export interface StatusChangeInput {
  status: RepairStatus;
  observations?: string;
  technical_diagnosis?: string;
  repair_description?: string;
  technician_name?: string;
  estimated_delivery_at?: string;
}

export const businessApi = {
  listClients: (query: Query = {}) => get<Page<Client>>(`/clients${toQuery(query)}`),
  getClient: (id: string) => get<Client>(`/clients/${id}`),
  createClient: (body: ClientInput) => send<Client>("POST", "/clients", body),
  updateClient: (id: string, body: Partial<ClientInput> & { is_active?: boolean }) =>
    send<Client>("PATCH", `/clients/${id}`, body),

  listEngines: (query: Query = {}) => get<Page<Engine>>(`/engines${toQuery(query)}`),
  getEngine: (id: string) => get<Engine>(`/engines/${id}`),
  createEngine: (body: EngineInput) => send<Engine>("POST", "/engines", body),
  updateEngine: (id: string, body: Partial<Omit<EngineInput, "serial_number">> & { is_active?: boolean }) =>
    send<Engine>("PATCH", `/engines/${id}`, body),

  listOrders: (query: Query = {}) => get<Page<RepairOrder>>(`/repair-orders${toQuery(query)}`),
  getOrder: (id: string) => get<RepairOrder>(`/repair-orders/${id}`),
  createOrder: (body: RepairOrderInput) => send<RepairOrder>("POST", "/repair-orders", body),
  changeStatus: (id: string, body: StatusChangeInput) =>
    send<RepairOrder>("PATCH", `/repair-orders/${id}/status`, body),
  recordApproval: (id: string, decision: "APPROVED" | "REJECTED", notes?: string) =>
    send<RepairOrder>("PATCH", `/repair-orders/${id}/approval`, { decision, notes }),
  history: (id: string) => get<StatusHistoryEntry[]>(`/repair-orders/${id}/history`),
  summary: () => get<StatusSummary>("/repair-orders/summary"),
};
