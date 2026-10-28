import { businessApi } from "../api/business-api";
import { useAsync } from "./useAsync";

/** Loads clients and engines for selects and name lookups (first 100 of each). */
export function useLookups() {
  const clients = useAsync(() => businessApi.listClients({ limit: 100 }), []);
  const engines = useAsync(() => businessApi.listEngines({ limit: 100 }), []);
  const clientName = (id: string) => clients.data?.items.find((c) => c.id === id)?.name ?? "—";
  const engineLabel = (id: string) => {
    const engine = engines.data?.items.find((e) => e.id === id);
    return engine ? `${engine.serial_number} · ${engine.manufacturer} ${engine.model}` : "—";
  };
  return { clients, engines, clientName, engineLabel };
}
