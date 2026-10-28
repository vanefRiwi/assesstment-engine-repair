import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";
import type { RepairStatus } from "../api/types";
import { STATUS_LABELS } from "../lib/labels";

export function Spinner({ label = "Cargando…" }: { label?: string }) {
  return (
    <div className="spinner" role="status">
      <span className="spinner-dot" aria-hidden /> {label}
    </div>
  );
}

export function Alert({ kind = "error", children }: { kind?: "error" | "success" | "info"; children: ReactNode }) {
  return (
    <div className={`alert alert-${kind}`} role={kind === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}

interface FieldProps {
  label: string;
  name: string;
  error?: string;
  children?: ReactNode;
}

function Field({ label, name, error, children }: FieldProps) {
  return (
    <label className="field" htmlFor={name}>
      <span>{label}</span>
      {children}
      {error && <small className="field-error">{error}</small>}
    </label>
  );
}

type InputFieldProps = InputHTMLAttributes<HTMLInputElement> & { label: string; name: string; error?: string };
export function InputField({ label, name, error, ...props }: InputFieldProps) {
  return (
    <Field label={label} name={name} error={error}>
      <input id={name} name={name} aria-invalid={Boolean(error)} {...props} />
    </Field>
  );
}

type TextareaFieldProps = TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; name: string; error?: string };
export function TextareaField({ label, name, error, ...props }: TextareaFieldProps) {
  return (
    <Field label={label} name={name} error={error}>
      <textarea id={name} name={name} rows={3} aria-invalid={Boolean(error)} {...props} />
    </Field>
  );
}

type SelectFieldProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  name: string;
  error?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
};
export function SelectField({ label, name, error, options, placeholder, ...props }: SelectFieldProps) {
  return (
    <Field label={label} name={name} error={error}>
      <select id={name} name={name} aria-invalid={Boolean(error)} {...props}>
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

export function StatusBadge({ status }: { status: RepairStatus }) {
  return <span className={`badge badge-${status.toLowerCase()}`}>{STATUS_LABELS[status]}</span>;
}

export function ActiveBadge({ active }: { active: boolean }) {
  return <span className={`badge ${active ? "badge-active" : "badge-inactive"}`}>{active ? "Activo" : "Inactivo"}</span>;
}

export function PageHeader({ title, actions }: { title: string; actions?: ReactNode }) {
  return (
    <div className="page-header">
      <h1>{title}</h1>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="empty">{children}</p>;
}

export function Pagination({
  total,
  limit,
  offset,
  onChange,
}: {
  total: number;
  limit: number;
  offset: number;
  onChange: (offset: number) => void;
}) {
  if (total <= limit) return null;
  const page = Math.floor(offset / limit) + 1;
  const pages = Math.ceil(total / limit);
  return (
    <div className="pagination">
      <button className="btn btn-secondary" disabled={offset === 0} onClick={() => onChange(offset - limit)}>
        Anterior
      </button>
      <span>
        Página {page} de {pages}
      </span>
      <button className="btn btn-secondary" disabled={page >= pages} onClick={() => onChange(offset + limit)}>
        Siguiente
      </button>
    </div>
  );
}
