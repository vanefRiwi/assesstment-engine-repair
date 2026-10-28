import { useState, type FormEvent } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { businessApi } from "../api/business-api";
import type { RepairStatus } from "../api/types";
import { Alert, InputField, PageHeader, SelectField, Spinner, StatusBadge, TextareaField } from "../components/ui";
import { errorMessage, localToIso } from "../lib/forms";
import { APPROVAL_LABELS, NEXT_STATUSES, STATUS_LABELS, formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";
import { useLookups } from "../lib/useLookups";

const EMPTY_CHANGE = {
  status: "",
  observations: "",
  technical_diagnosis: "",
  repair_description: "",
  technician_name: "",
  estimated_delivery_at: "",
};

export function OrderDetailPage() {
  const { id = "" } = useParams();
  const location = useLocation();
  const { clientName, engineLabel } = useLookups();
  const order = useAsync(() => businessApi.getOrder(id), [id]);
  const history = useAsync(() => businessApi.history(id), [id]);

  const [change, setChange] = useState(EMPTY_CHANGE);
  const [approvalNotes, setApprovalNotes] = useState("");
  const [message, setMessage] = useState<{ kind: "success" | "error"; text: string } | null>(
    (location.state as { created?: boolean } | null)?.created ? { kind: "success", text: "Orden creada." } : null,
  );
  const [saving, setSaving] = useState(false);

  async function run(action: () => Promise<unknown>, successText: string) {
    setSaving(true);
    setMessage(null);
    try {
      await action();
      setMessage({ kind: "success", text: successText });
      await Promise.all([order.reload(), history.reload()]);
    } catch (err) {
      setMessage({ kind: "error", text: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  function handleStatus(event: FormEvent) {
    event.preventDefault();
    if (!change.status) {
      setMessage({ kind: "error", text: "Selecciona el nuevo estado." });
      return;
    }
    const optional = (value: string) => value.trim() || undefined;
    void run(async () => {
      await businessApi.changeStatus(id, {
        status: change.status as RepairStatus,
        observations: optional(change.observations),
        technical_diagnosis: optional(change.technical_diagnosis),
        repair_description: optional(change.repair_description),
        technician_name: optional(change.technician_name),
        estimated_delivery_at: localToIso(change.estimated_delivery_at),
      });
      setChange(EMPTY_CHANGE);
    }, `Estado actualizado a "${STATUS_LABELS[change.status as RepairStatus]}".`);
  }

  if (order.loading && !order.data) return <Spinner />;
  if (order.error || !order.data) return <Alert>{order.error ?? "Orden no encontrada."}</Alert>;
  const data = order.data;
  const nextStatuses = NEXT_STATUSES[data.status];
  const approvalPending = data.status === "AWAITING_APPROVAL";

  return (
    <>
      <PageHeader title={`Orden ${data.order_number}`} actions={<StatusBadge status={data.status} />} />
      {message && <Alert kind={message.kind}>{message.text}</Alert>}
      <div className="two-cols">
        <div className="card">
          <h2>Información de la reparación</h2>
          <dl className="details">
            <dt>Cliente</dt><dd><Link to={`/clients/${data.client_id}`}>{clientName(data.client_id)}</Link></dd>
            <dt>Motor</dt><dd><Link to={`/engines/${data.engine_id}`}>{engineLabel(data.engine_id)}</Link></dd>
            <dt>Recepción</dt><dd>{formatDate(data.received_at)}</dd>
            <dt>Problema reportado</dt><dd>{data.reported_problem}</dd>
            <dt>Diagnóstico técnico</dt><dd>{data.technical_diagnosis ?? "—"}</dd>
            <dt>Trabajo realizado / requerido</dt><dd>{data.repair_description ?? "—"}</dd>
            <dt>Técnico responsable</dt><dd>{data.technician_name ?? "—"}</dd>
            <dt>Entrega estimada</dt><dd>{formatDate(data.estimated_delivery_at)}</dd>
            <dt>Entrega real</dt><dd>{formatDate(data.actual_delivery_at)}</dd>
            <dt>Aprobación del cliente</dt>
            <dd>
              {APPROVAL_LABELS[data.approval_status]}
              {data.approved_at && ` · ${formatDate(data.approved_at)}`}
              {data.approval_notes && ` · ${data.approval_notes}`}
            </dd>
            <dt>Observaciones</dt><dd>{data.observations ?? "—"}</dd>
            <dt>Creada</dt><dd>{formatDate(data.created_at)}</dd>
            <dt>Última actualización</dt><dd>{formatDate(data.updated_at)}</dd>
          </dl>
        </div>

        <div>
          {approvalPending && (
            <div className="card">
              <h2>Aprobación del cliente</h2>
              <p>La reparación solo puede iniciar cuando el cliente la aprueba.</p>
              <TextareaField label="Notas de la decisión" name="approvalNotes" value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)} />
              <div className="form-actions">
                <button className="btn" disabled={saving}
                  onClick={() => run(() => businessApi.recordApproval(id, "APPROVED", approvalNotes || undefined), "Aprobación registrada.")}>
                  Registrar aprobación
                </button>
                <button className="btn btn-danger" disabled={saving}
                  onClick={() => run(() => businessApi.recordApproval(id, "REJECTED", approvalNotes || undefined), "Rechazo registrado.")}>
                  Registrar rechazo
                </button>
              </div>
            </div>
          )}

          {nextStatuses.length > 0 && (
            <form className="card" onSubmit={handleStatus} noValidate>
              <h2>Actualizar estado</h2>
              <SelectField label="Nuevo estado" name="status" value={change.status} placeholder="Selecciona…"
                options={nextStatuses.map((s) => ({ value: s, label: STATUS_LABELS[s] }))}
                onChange={(e) => setChange({ ...change, status: e.target.value })} />
              <TextareaField label="Observaciones del cambio" name="observations" value={change.observations}
                onChange={(e) => setChange({ ...change, observations: e.target.value })} />
              <TextareaField label="Diagnóstico técnico" name="technical_diagnosis" value={change.technical_diagnosis}
                placeholder={data.technical_diagnosis ?? ""}
                onChange={(e) => setChange({ ...change, technical_diagnosis: e.target.value })} />
              <TextareaField label="Trabajo realizado / requerido" name="repair_description" value={change.repair_description}
                placeholder={data.repair_description ?? ""}
                onChange={(e) => setChange({ ...change, repair_description: e.target.value })} />
              <InputField label="Técnico responsable" name="technician_name" value={change.technician_name}
                placeholder={data.technician_name ?? ""}
                onChange={(e) => setChange({ ...change, technician_name: e.target.value })} />
              <InputField label="Fecha estimada de entrega" name="estimated_delivery_at" type="datetime-local"
                value={change.estimated_delivery_at}
                onChange={(e) => setChange({ ...change, estimated_delivery_at: e.target.value })} />
              <div className="form-actions">
                <button className="btn" type="submit" disabled={saving}>{saving ? "Guardando…" : "Actualizar estado"}</button>
              </div>
            </form>
          )}

          <div className="card">
            <h2>Historial de estados</h2>
            {history.loading ? (
              <Spinner />
            ) : (
              <ul className="timeline">
                {history.data?.map((entry) => (
                  <li key={entry.id}>
                    <StatusBadge status={entry.status} />
                    <small>{formatDate(entry.changed_at)}</small>
                    {entry.observations && <div>{entry.observations}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
