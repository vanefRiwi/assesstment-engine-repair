import { useCallback, useEffect, useState } from "react";
import { errorMessage } from "./forms";

/** Loads data on mount and whenever deps change; exposes loading, error and a reload function. */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const load = useCallback(loader, deps);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await load());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [load]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, loading, error, reload, setData };
}
