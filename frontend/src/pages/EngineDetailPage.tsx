import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { ActiveBadge, Alert, EmptyState, InputField, PageHeader, Spinner, StatusBadge } from "../components/ui";
import { apiFieldErrors, engineSchema, errorMessage, validate, type FieldErrors } from "../lib/forms";
import { formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";
import { useLookups } from "../lib/useLookups";

const editSchema = engineSchema.pick({ manufacturer: true, model: true, engine_type: true, capacity: true });

export function EngineDetailPage() {
  const { id = "" } = useParams();
  const { clientName } = useLookups();
  const engine = useAsync(() => businessApi.getEngine(id), [id]);
  const orders = useAsync(() => businessApi.listOrders({ engine_id: id, limit: 50 }), [id]);

  const [values, setValues] = useState({ manufacturer: "", model: "", engine_type: "", capacity: "" });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (engine.data) {
      const { manufacturer, model, engine_type, capacity } = engine.data;
      setValues({ manufacturer, model, engine_type, capacity: capacity ?? "" });
    }
  }, [engine.data]);

  async function save(changes: Parameters<typeof businessApi.updateEngine>[1], successText: string) {
    setSaving(true);
    setMessage(null);
    try {
      engine.setData(await businessApi.updateEngine(id, changes));
      setMessage({ kind: "success", text: successText });
    } catch (err) {
      setErrors(apiFieldErrors(err));
      setMessage({ kind: "error", text: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = validate(editSchema, values);
    setErrors(result.errors ?? {});
    if (result.data) await save(result.data, "Motor actualizado.");
  }

  if (engine.loading) return <Spinner />;
  if (engine.error || !engine.data) return <Alert>{engine.error ?? "Motor no encontrado."}</Alert>;
  const data = engine.data;
  const field = (name: keyof typeof values, label: string) => (
    <InputField label={label} name={name} value={values[name]} error={errors[name]}
      onChange={(e) => setValues({ ...values, [name]: e.target.value })} />
  );

  return (
    <>
      <PageHeader
        title={`Motor ${data.serial_number}`}
        actions={
          <>
            <Link className="btn btn-secondary" to={`/orders/new?engine=${data.id}`}>Nueva orden</Link>
            <button className={`btn ${data.is_active ? "btn-danger" : ""}`} disabled={saving}
              onClick={() => save({ is_active: !data.is_active }, data.is_active ? "Motor desactivado." : "Motor activado.")}>
              {data.is_active ? "Desactivar" : "Activar"}
            </button>
          </>
        }
      />
      {message && <Alert kind={message.kind}>{message.text}</Alert>}
      <div className="two-cols">
        <div className="card">
          <h2>Información</h2>
          <dl className="details">
            <dt>Cliente</dt>
            <dd><Link to={`/clients/${data.client_id}`}>{clientName(data.client_id)}</Link></dd>
            <dt>Fabricante</dt><dd>{data.manufacturer}</dd>
            <dt>Modelo</dt><dd>{data.model}</dd>
            <dt>Tipo</dt><dd>{data.engine_type}</dd>
            <dt>Capacidad</dt><dd>{data.capacity ?? "—"}</dd>
            <dt>Registro</dt><dd>{formatDate(data.registered_at)}</dd>
            <dt>Estado</dt><dd><ActiveBadge active={data.is_active} /></dd>
          </dl>
        </div>
        <form className="card" onSubmit={handleSubmit} noValidate>
          <h2>Editar motor</h2>
          {field("manufacturer", "Fabricante")}
          {field("model", "Modelo")}
          {field("engine_type", "Tipo de motor")}
          {field("capacity", "Potencia o capacidad")}
          <div className="form-actions">
            <button className="btn" type="submit" disabled={saving}>Guardar cambios</button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Historial de reparaciones</h2>
        {orders.loading ? (
          <Spinner />
        ) : orders.data?.items.length ? (
          <ul>
            {orders.data.items.map((order) => (
              <li key={order.id}>
                <Link to={`/orders/${order.id}`}>{order.order_number}</Link> · {formatDate(order.received_at)} ·{" "}
                <StatusBadge status={order.status} />
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState>Este motor no tiene órdenes de reparación.</EmptyState>
        )}
      </div>
    </>
  );
}
