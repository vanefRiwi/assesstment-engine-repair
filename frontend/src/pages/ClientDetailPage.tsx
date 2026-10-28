import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { ActiveBadge, Alert, EmptyState, InputField, PageHeader, Spinner } from "../components/ui";
import { apiFieldErrors, clientSchema, errorMessage, validate, type FieldErrors } from "../lib/forms";
import { formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";

const editSchema = clientSchema.pick({ name: true, email: true, phone: true });

export function ClientDetailPage() {
  const { id = "" } = useParams();
  const client = useAsync(() => businessApi.getClient(id), [id]);
  const engines = useAsync(() => businessApi.listEngines({ client_id: id, limit: 100 }), [id]);

  const [values, setValues] = useState({ name: "", email: "", phone: "" });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (client.data) {
      setValues({ name: client.data.name, email: client.data.email ?? "", phone: client.data.phone ?? "" });
    }
  }, [client.data]);

  async function save(changes: Parameters<typeof businessApi.updateClient>[1], successText: string) {
    setSaving(true);
    setMessage(null);
    try {
      client.setData(await businessApi.updateClient(id, changes));
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
    if (result.data) await save(result.data, "Cliente actualizado.");
  }

  if (client.loading) return <Spinner />;
  if (client.error || !client.data) return <Alert>{client.error ?? "Cliente no encontrado."}</Alert>;
  const data = client.data;

  return (
    <>
      <PageHeader
        title={data.name}
        actions={
          <button
            className={`btn ${data.is_active ? "btn-danger" : ""}`}
            disabled={saving}
            onClick={() => save({ is_active: !data.is_active }, data.is_active ? "Cliente desactivado." : "Cliente activado.")}
          >
            {data.is_active ? "Desactivar" : "Activar"}
          </button>
        }
      />
      {message && <Alert kind={message.kind}>{message.text}</Alert>}
      <div className="two-cols">
        <div className="card">
          <h2>Información</h2>
          <dl className="details">
            <dt>Documento</dt>
            <dd>
              {data.document_type} {data.document_number}
            </dd>
            <dt>Estado</dt>
            <dd>
              <ActiveBadge active={data.is_active} />
            </dd>
            <dt>Registrado</dt>
            <dd>{formatDate(data.created_at)}</dd>
            <dt>Actualizado</dt>
            <dd>{formatDate(data.updated_at)}</dd>
          </dl>
        </div>
        <form className="card" onSubmit={handleSubmit} noValidate>
          <h2>Editar cliente</h2>
          <InputField label="Nombre o razón social" name="name" value={values.name} error={errors.name}
            onChange={(e) => setValues({ ...values, name: e.target.value })} />
          <InputField label="Correo electrónico" name="email" type="email" value={values.email} error={errors.email}
            onChange={(e) => setValues({ ...values, email: e.target.value })} />
          <InputField label="Teléfono" name="phone" value={values.phone} error={errors.phone}
            onChange={(e) => setValues({ ...values, phone: e.target.value })} />
          <div className="form-actions">
            <button className="btn" type="submit" disabled={saving}>Guardar cambios</button>
          </div>
        </form>
      </div>
      <div className="card">
        <h2>Motores del cliente</h2>
        {engines.loading ? (
          <Spinner />
        ) : engines.data?.items.length ? (
          <ul>
            {engines.data.items.map((engine) => (
              <li key={engine.id}>
                <Link to={`/engines/${engine.id}`}>{engine.serial_number}</Link> · {engine.manufacturer} {engine.model}
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState>Este cliente no tiene motores registrados.</EmptyState>
        )}
      </div>
    </>
  );
}
