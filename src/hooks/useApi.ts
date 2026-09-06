import { useCallback, useEffect, useState } from "react";
import type { AxiosResponse } from "axios";
import { apiError, http } from "../services/api";

type State<T> = {
  status: "idle" | "loading" | "error" | "success";
  data: T | null;
  error: string | null;
};

const initial = <T,>(): State<T> => ({ status: "idle", data: null, error: null });

/** Minimal data-fetch hook. Pass a URL (or null to skip) for auto-fetch. */
export function useApi<T>(url: string | null, auto = true) {
  const [state, setState] = useState<State<T>>(() => initial<T>());

  const run = useCallback(async () => {
    if (!url) return;
    setState((s) => ({ ...s, status: "loading", error: null }));
    try {
      const { data }: AxiosResponse<T> = await http.get<T>(url);
      setState({ status: "success", data, error: null });
    } catch (e) {
      setState({ status: "error", data: null, error: apiError(e as never) });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  useEffect(() => {
    if (auto) void run();
  }, [auto, run]);

  const refresh = useCallback(() => void run(), [run]);
  return { ...state, refetch: refresh };
}

/** Fetch a paginated list; returns the `results` array plus count. */
export function useList<T>(url: string | null, auto = true) {
  const api = useApi<{ count: number; results: T[] } | T[]>(url, auto);
  const results = Array.isArray(api.data) ? api.data : api.data?.results ?? [];
  const count = Array.isArray(api.data) ? results.length : api.data?.count ?? 0;
  return { ...api, data: results, count };
}

