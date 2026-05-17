export class ApiError extends Error {
  constructor(public message: string, public status: number, public payload: any = null) {
    super(message);
    this.name = "ApiError";
  }
}

export const apiClient = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });

  if (!res.ok) {
    let payload = null;
    try { payload = await res.json(); } catch (_) {}
    throw new ApiError(payload?.detail || payload?.message || "Request failed", res.status, payload);
  }

  if (res.status === 204) return null as T;
  const text = await res.text();
  return text ? JSON.parse(text) : (null as T);
};

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const fetchWithBackoff = async <T>(fn: () => Promise<T>, retries = 3, delay = 500): Promise<T> => {
  try { return await fn(); } catch (err: any) {
    const isRetryable = !(err.name === "AbortError") && (!(err instanceof ApiError) || err.status >= 500);
    if (retries <= 0 || !isRetryable) throw err;
    await sleep(delay * 2 + Math.random() * 100);
    return fetchWithBackoff(fn, retries - 1, delay * 2);
  }
};
