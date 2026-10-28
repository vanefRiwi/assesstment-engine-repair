import { z } from "zod";
import { ApiError } from "../api/http";

export type FieldErrors = Record<string, string>;

/** Validates form values with zod and returns the parsed data or a map of field messages. */
export function validate<T extends z.ZodTypeAny>(
  schema: T,
  values: unknown,
): { data: z.infer<T>; errors: null } | { data: null; errors: FieldErrors } {
  const result = schema.safeParse(values);
  if (result.success) return { data: result.data, errors: null };
  const errors: FieldErrors = {};
  for (const issue of result.error.issues) errors[issue.path.join(".")] ??= issue.message;
  return { data: null, errors };
}

/** Field errors returned by the API (422) merged into the same shape. */
export function apiFieldErrors(error: unknown): FieldErrors {
  if (!(error instanceof ApiError)) return {};
  return Object.fromEntries(error.fieldErrors.map((issue) => [issue.field, issue.message]));
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}

const optionalText = (max: number) =>
  z
    .string()
    .trim()
    .max(max, `Máximo ${max} caracteres`)
    .transform((value) => value || undefined);

export const clientSchema = z.object({
  name: z.string().trim().min(2, "Ingresa el nombre o razón social").max(150),
  document_type: z.string().trim().min(1, "Selecciona el tipo de documento"),
  document_number: z.string().trim().min(3, "Mínimo 3 caracteres").max(40),
  email: z.union([z.literal(""), z.string().trim().email("Correo no válido")]).transform((v) => v || undefined),
  phone: optionalText(30),
});

export const engineSchema = z.object({
  serial_number: z.string().trim().min(3, "Mínimo 3 caracteres").max(100),
  manufacturer: z.string().trim().min(1, "Ingresa el fabricante").max(100),
  model: z.string().trim().min(1, "Ingresa el modelo").max(100),
  engine_type: z.string().trim().min(1, "Ingresa el tipo de motor").max(60),
  capacity: optionalText(60),
  client_id: z.string().uuid("Selecciona el cliente propietario"),
});

export const orderSchema = z.object({
  engine_id: z.string().uuid("Selecciona el motor"),
  received_at: z.string().min(1, "Ingresa la fecha de recepción"),
  reported_problem: z.string().trim().min(5, "Describe el problema (mínimo 5 caracteres)").max(5000),
  technician_name: optionalText(120),
  estimated_delivery_at: z.string().transform((v) => v || undefined),
  observations: optionalText(5000),
});

export const userSchema = z.object({
  name: z.string().trim().min(2, "Ingresa el nombre").max(120),
  email: z.string().trim().email("Correo no válido"),
  password: z.string().min(8, "Mínimo 8 caracteres").max(128),
  role: z.enum(["ADMIN", "OPERATOR"]),
});

/** Converts a datetime-local input value to an ISO string with timezone. */
export function localToIso(value: string | undefined): string | undefined {
  return value ? new Date(value).toISOString() : undefined;
}
