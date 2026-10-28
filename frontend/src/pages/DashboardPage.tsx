import { Link } from "react-router-dom";
import { businessApi } from "../api/business-api";
import { REPAIR_STATUSES } from "../api/types";
import { Alert, EmptyState, PageHeader, Spinner, StatusBadge } from "../components/ui";
import { STATUS_LABELS, formatDate } from "../lib/labels";
import { useAsync } from "../lib/useAsync";

export function DashboardPage() {
  const summary = useAsync(() => businessApi.summary(), []);
  const recent = useAsync(() => businessApi.listOrders({ limit: 5 }), []);

  return (
    <>
      <PageHeader
        title="Dashboard"
        actions={
          <Link className="btn" to="/orders/new">
            Nueva orden
          </Link>
        }
      />
      {summary.error && <Alert>{summary.error}</Alert>}
      {summary.loading ? (
        <Spinner />
      ) : (
        summary.data && (
          <div className="grid" style={{ marginBottom: "1.25rem" }}>
            <div className="card stat">
              <strong>{summary.data.total}</strong>
              Órdenes totales
            </div>
            {REPAIR_STATUSES.map((status) => (
              <div key={status} className="card stat">
                <Link to={`/orders?status=${status}`}>
                  <strong>{summary.data!.by_status[status] ?? 0}</strong>
                  {STATUS_LABELS[status]}
                </Link>
              </div>
            ))}
          </div>
        )
      )}

      <div className="card">
        <h2>Órdenes recientes</h2>
        {recent.error && <Alert>{recent.error}</Alert>}
        {recent.loading ? (
          <Spinner />
        ) : recent.data?.items.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Orden</th>
                  <th>Problema reportado</th>
                  <th>Recepción</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {recent.data.items.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <Link to={`/orders/${order.id}`}>{order.order_number}</Link>
                    </td>
                    <td>{order.reported_problem}</td>
                    <td>{formatDate(order.received_at)}</td>
                    <td>
                      <StatusBadge status={order.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState>Aún no hay órdenes registradas.</EmptyState>
        )}
      </div>
    </>
  );
}
