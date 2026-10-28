export type Role = "ADMIN" | "OPERATOR";

export const REPAIR_STATUSES = [
  "RECEIVED",
  "IN_DIAGNOSIS",
  "AWAITING_APPROVAL",
  "IN_REPAIR",
  "IN_TESTING",
  "COMPLETED",
  "DELIVERED",
] as const;
export type RepairStatus = (typeof REPAIR_STATUSES)[number];
export type ApprovalStatus = "NOT_REQUIRED" | "PENDING" | "APPROVED" | "REJECTED";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Client {
  id: string;
  name: string;
  document_type: string;
  document_number: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Engine {
  id: string;
  serial_number: string;
  manufacturer: string;
  model: string;
  engine_type: string;
  capacity: string | null;
  client_id: string;
  registered_at: string;
  is_active: boolean;
}

export interface RepairOrder {
  id: string;
  order_number: string;
  engine_id: string;
  client_id: string;
  received_at: string;
  reported_problem: string;
  technical_diagnosis: string | null;
  repair_description: string | null;
  technician_name: string | null;
  estimated_delivery_at: string | null;
  actual_delivery_at: string | null;
  status: RepairStatus;
  approval_status: ApprovalStatus;
  approved_at: string | null;
  approval_notes: string | null;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface StatusHistoryEntry {
  id: string;
  status: RepairStatus;
  changed_by: string | null;
  changed_at: string;
  observations: string | null;
}

export interface StatusSummary {
  total: number;
  by_status: Record<RepairStatus, number>;
}
