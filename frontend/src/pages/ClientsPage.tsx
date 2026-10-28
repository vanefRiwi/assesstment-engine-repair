import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { ActiveBadge, Alert, EmptyState, InputField, PageHeader, Pagination, SelectField, Spinner } from "../components/ui";
import { apiFieldErrors, clientSchema, errorMessage, validate, type FieldErrors } from "../lib/forms";
import { useAsync } from "../lib/useAsync";

export const DOCUMENT_TYPES = [
  { value: "NIT", label: "NIT" },
  { value: "CC", label: "Cédula de ciudadanía" },
  { value: "CE", label: "Cédula de extranjería" },
  { value: "PASSPORT", label: "Pasaporte" },
];

const EMPTY = { name: "", document_type: "NIT", document_number: "", email: "", phone: "" };
const LIMIT = 20;

export function ClientsPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const list = useAsync(() => businessApi.listClients({ q: search, limit: LIMIT, offset }), [search, offset]);

  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    const result = validate(clientSchema, values);
    setErrors(result.errors ?? {});
    if (!result.data) return;

    setSaving(true);
    setMessage(null);
    try {
      const client = await businessApi.createClient(result.data);
      setValues(EMPTY);
      setMessage({ kind: "success", text: `Cliente "${client.name}" registrado.` });
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
      <PageHeader title="Clientes" />
      <form className="card" onSubmit={handleCreate} noValidate>
        <h2>Registrar cliente</h2>
        {message && <Alert kind={message.kind}>{message.text}</Alert>}
        <div className="grid">
          <InputField label="Nombre o razón social *" {...field("name")} />
          <SelectField label="Tipo de documento *" options={DOCUMENT_TYPES} {...field("document_type")} />
          <InputField label="Número de documento *" {...field("document_number")} />
          <InputField label="Correo electrónico" type="email" {...field("email")} />
          <InputField label="Teléfono" {...field("phone")} />
        </div>
        <div className="form-actions">
          <button className="btn" type="submit" disabled={saving}>
            {saving ? "Guardando…" : "Registrar cliente"}
          </button>
        </div>
      </form>

      <div className="card">
        <div className="filters">
          <InputField
            label="Buscar por nombre o documento"
            name="search"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setOffset(0);
            }}
          />
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
                    <th>Nombre</th>
                    <th>Documento</th>
                    <th>Correo</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((client) => (
                    <tr key={client.id}>
                      <td>
                        <Link to={`/clients/${client.id}`}>{client.name}</Link>
                      </td>
                      <td>
                        {client.document_type} {client.document_number}
                      </td>
                      <td>{client.email ?? "—"}</td>
                      <td>
                        <ActiveBadge active={client.is_active} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination total={list.data.total} limit={LIMIT} offset={offset} onChange={setOffset} />
          </>
        ) : (
          <EmptyState>No hay clientes que coincidan.</EmptyState>
        )}
      </div>
    </>
  );
}
