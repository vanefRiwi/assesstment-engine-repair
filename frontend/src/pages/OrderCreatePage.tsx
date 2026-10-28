import { useState, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { Alert, InputField, PageHeader, SelectField, TextareaField } from "../components/ui";
import { apiFieldErrors, errorMessage, localToIso, orderSchema, validate, type FieldErrors } from "../lib/forms";
import { useLookups } from "../lib/useLookups";

function nowLocal(): string {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

export function OrderCreatePage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { engines, clientName } = useLookups();
  const [values, setValues] = useState({
    engine_id: params.get("engine") ?? "",
    received_at: nowLocal(),
    reported_problem: "",
    technician_name: "",
    estimated_delivery_at: "",
    observations: "",
  });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const activeEngines = (engines.data?.items ?? []).filter((e) => e.is_active);
  const selected = activeEngines.find((e) => e.id === values.engine_id);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = validate(orderSchema, values);
    setErrors(result.errors ?? {});
    if (!result.data) return;

    setSaving(true);
    setError(null);
    try {
      const order = await businessApi.createOrder({
        ...result.data,
        received_at: localToIso(result.data.received_at)!,
        estimated_delivery_at: localToIso(result.data.estimated_delivery_at),
      });
      navigate(`/orders/${order.id}`, { state: { created: true } });
    } catch (err) {
      setErrors(apiFieldErrors(err));
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  const field = (name: keyof typeof values) => ({
    name,
    value: values[name],
    error: errors[name],
    onChange: (e: { target: { value: string } }) => setValues({ ...values, [name]: e.target.value }),
  });

  return (
    <>
      <PageHeader title="Nueva orden de reparación" />
      <form className="card" onSubmit={handleSubmit} noValidate>
        {error && <Alert>{error}</Alert>}
        <div className="grid">
          <SelectField label="Motor *" placeholder="Selecciona…" {...field("engine_id")}
            options={activeEngines.map((e) => ({ value: e.id, label: `${e.serial_number} · ${e.manufacturer} ${e.model}` }))} />
          <InputField label="Cliente propietario" name="client" readOnly
            value={selected ? clientName(selected.client_id) : "Se toma del motor"} />
          <InputField label="Fecha de recepción *" type="datetime-local" {...field("received_at")} />
          <InputField label="Fecha estimada de entrega" type="datetime-local" {...field("estimated_delivery_at")} />
          <InputField label="Técnico responsable" {...field("technician_name")} />
        </div>
        <TextareaField label="Problema reportado *" {...field("reported_problem")} />
        <TextareaField label="Observaciones" {...field("observations")} />
        <div className="form-actions">
          <button className="btn" type="submit" disabled={saving}>{saving ? "Creando…" : "Crear orden"}</button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate(-1)}>Cancelar</button>
        </div>
      </form>
    </>
  );
}
