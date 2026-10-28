import type { ApprovalStatus, RepairStatus } from "../api/types";

export const STATUS_LABELS: Record<RepairStatus, string> = {
  RECEIVED: "Recibido",
  IN_DIAGNOSIS: "En diagnóstico",
  AWAITING_APPROVAL: "Esperando aprobación",
  IN_REPAIR: "En reparación",
  IN_TESTING: "En pruebas",
  COMPLETED: "Finalizado",
  DELIVERED: "Entregado",
};

export const APPROVAL_LABELS: Record<ApprovalStatus, string> = {
  NOT_REQUIRED: "No requerida",
  PENDING: "Pendiente",
  APPROVED: "Aprobada",
  REJECTED: "Rechazada",
};

/** Mirrors the backend transition rules so the UI only offers valid next steps. */
export const NEXT_STATUSES: Record<RepairStatus, RepairStatus[]> = {
  RECEIVED: ["IN_DIAGNOSIS"],
  IN_DIAGNOSIS: ["AWAITING_APPROVAL"],
  AWAITING_APPROVAL: ["IN_REPAIR", "IN_DIAGNOSIS"],
  IN_REPAIR: ["IN_TESTING"],
  IN_TESTING: ["COMPLETED", "IN_REPAIR"],
  COMPLETED: ["DELIVERED"],
  DELIVERED: [],
};

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}
