import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { REPAIR_STATUSES } from "../api/types";
import { Alert, EmptyState, InputField, PageHeader, Pagination, SelectField, Spinner, StatusBadge } from "../components/ui";
import { STATUS_LABELS, formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";
import { useLookups } from "../lib/useLookups";

const LIMIT = 20;

export function OrdersPage() {
  const { clients, engines, clientName, engineLabel } = useLookups();
  // Filters live in the URL so they survive reloads and can be linked from the dashboard.
  const [params, setParams] = useSearchParams();
  const [offset, setOffset] = useState(0);
  const filters = {
    status: params.get("status") ?? "",
    client_id: params.get("client_id") ?? "",
    engine_id: params.get("engine_id") ?? "",
    q: params.get("q") ?? "",
  };
  const list = useAsync(
    () => businessApi.listOrders({ ...filters, limit: LIMIT, offset }),
    [filters.status, filters.client_id, filters.engine_id, filters.q, offset],
  );

  function setFilter(name: keyof typeof filters, value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(name, value);
    else next.delete(name);
    setParams(next, { replace: true });
    setOffset(0);
  }

  const engineOptions = (engines.data?.items ?? [])
    .filter((e) => !filters.client_id || e.client_id === filters.client_id)
    .map((e) => ({ value: e.id, label: e.serial_number }));

  return (
    <>
      <PageHeader title="Órdenes de reparación" actions={<Link className="btn" to="/orders/new">Nueva orden</Link>} />
      <div className="card">
        <div className="filters">
          <InputField label="Buscar (número, problema, técnico)" name="q" value={filters.q}
            onChange={(e) => setFilter("q", e.target.value)} />
          <SelectField label="Estado" name="status" value={filters.status} placeholder="Todos"
            options={REPAIR_STATUSES.map((s) => ({ value: s, label: STATUS_LABELS[s] }))}
            onChange={(e) => setFilter("status", e.target.value)} />
          <SelectField label="Cliente" name="client_id" value={filters.client_id} placeholder="Todos"
            options={(clients.data?.items ?? []).map((c) => ({ value: c.id, label: c.name }))}
            onChange={(e) => setFilter("client_id", e.target.value)} />
          <SelectField label="Motor" name="engine_id" value={filters.engine_id} placeholder="Todos"
            options={engineOptions} onChange={(e) => setFilter("engine_id", e.target.value)} />
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
                    <th>Orden</th>
                    <th>Cliente</th>
                    <th>Motor</th>
                    <th>Recepción</th>
                    <th>Entrega estimada</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((order) => (
                    <tr key={order.id}>
                      <td><Link to={`/orders/${order.id}`}>{order.order_number}</Link></td>
                      <td>{clientName(order.client_id)}</td>
                      <td>{engineLabel(order.engine_id)}</td>
                      <td>{formatDate(order.received_at)}</td>
                      <td>{formatDate(order.estimated_delivery_at)}</td>
                      <td><StatusBadge status={order.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination total={list.data.total} limit={LIMIT} offset={offset} onChange={setOffset} />
          </>
        ) : (
          <EmptyState>No hay órdenes que coincidan con los filtros.</EmptyState>
        )}
      </div>
    </>
  );
}
