import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { ActiveBadge, Alert, EmptyState, InputField, PageHeader, Pagination, SelectField, Spinner } from "../components/ui";
import { apiFieldErrors, engineSchema, errorMessage, validate, type FieldErrors } from "../lib/forms";
import { useAsync } from "../lib/useAsync";
import { useLookups } from "../lib/useLookups";

const EMPTY = { serial_number: "", manufacturer: "", model: "", engine_type: "", capacity: "", client_id: "" };
const LIMIT = 20;

export function EnginesPage() {
  const { clients, clientName } = useLookups();
  const [search, setSearch] = useState("");
  const [clientFilter, setClientFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const list = useAsync(
    () => businessApi.listEngines({ q: search, client_id: clientFilter || undefined, limit: LIMIT, offset }),
    [search, clientFilter, offset],
  );

  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  const clientOptions = (clients.data?.items ?? [])
    .filter((c) => c.is_active)
    .map((c) => ({ value: c.id, label: `${c.name} (${c.document_number})` }));

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    const result = validate(engineSchema, values);
    setErrors(result.errors ?? {});
    if (!result.data) return;

    setSaving(true);
    setMessage(null);
    try {
      const engine = await businessApi.createEngine(result.data);
      setValues(EMPTY);
      setMessage({ kind: "success", text: `Motor ${engine.serial_number} registrado.` });
      void list.reload();
    } catch (err) {
      setErrors(apiFieldErrors(err));
      setMessage({ kind: "error", text: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  const field = (name: keyof typeof EMPTY) => ({
    name,
    value: values[name],
    error: errors[name],
    onChange: (e: { target: { value: string } }) => setValues({ ...values, [name]: e.target.value }),
  });

  return (
    <>
      <PageHeader title="Motores" />
      <form className="card" onSubmit={handleCreate} noValidate>
        <h2>Registrar motor</h2>
        {message && <Alert kind={message.kind}>{message.text}</Alert>}
        <div className="grid">
          <InputField label="Código interno o número de serie *" {...field("serial_number")} />
          <InputField label="Fabricante *" {...field("manufacturer")} />
          <InputField label="Modelo *" {...field("model")} />
          <InputField label="Tipo de motor *" {...field("engine_type")} />
          <InputField label="Potencia o capacidad" {...field("capacity")} />
          <SelectField label="Cliente propietario *" options={clientOptions} placeholder="Selecciona…" {...field("client_id")} />
        </div>
        <div className="form-actions">
          <button className="btn" type="submit" disabled={saving}>
            {saving ? "Guardando…" : "Registrar motor"}
          </button>
        </div>
      </form>

      <div className="card">
        <div className="filters">
          <InputField label="Buscar por serie, fabricante o modelo" name="search" value={search}
            onChange={(e) => { setSearch(e.target.value); setOffset(0); }} />
          <SelectField label="Cliente" name="clientFilter" value={clientFilter} placeholder="Todos"
            options={(clients.data?.items ?? []).map((c) => ({ value: c.id, label: c.name }))}
            onChange={(e) => { setClientFilter(e.target.value); setOffset(0); }} />
        </div>
        {list.error && <Alert>{list.error}</Alert>}
        {list.loading ? (
          <Spinner />
        ) : list.data?.items.length ? (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Serie</th>
                    <th>Fabricante / modelo</th>
                    <th>Tipo</th>
                    <th>Cliente</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((engine) => (
                    <tr key={engine.id}>
                      <td><Link to={`/engines/${engine.id}`}>{engine.serial_number}</Link></td>
                      <td>{engine.manufacturer} {engine.model}</td>
                      <td>{engine.engine_type}</td>
                      <td>{clientName(engine.client_id)}</td>
                      <td><ActiveBadge active={engine.is_active} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination total={list.data.total} limit={LIMIT} offset={offset} onChange={setOffset} />
          </>
        ) : (
          <EmptyState>No hay motores que coincidan.</EmptyState>
        )}
      </div>
    </>
  );
}
