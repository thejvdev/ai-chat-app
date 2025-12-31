import type { ApiError } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

function toUrl(path: string) {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_URL}${p}`;
}

async function parseOkBody(res: Response): Promise<unknown> {
  if (res.status === 204 || res.status === 205) return null;

  const ct = res.headers.get("content-type")?.toLowerCase() ?? "";
  if (ct.includes("json")) return (await res.json()) as unknown;
  return (await res.text()) as unknown;
}

async function readErrorDetail(res: Response): Promise<string> {
  const ct = res.headers.get("content-type")?.toLowerCase() ?? "";
  if (ct.includes("json")) {
    const data = (await res.json()) as { detail: string };
    return data.detail;
  }

  const text = await res.text();
  return text || "Request failed";
}

async function throwApiError(res: Response): Promise<never> {
  const detail = await readErrorDetail(res);
  throw { status: res.status, data: { detail } } satisfies ApiError;
}

export async function GET<T>(path: string): Promise<T> {
  const res = await fetch(toUrl(path), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseOkBody(res);
  return data as T;
}

export async function POST<
  TResponse,
  TBody extends object | undefined = object | undefined
>(path: string, body?: TBody): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "POST",
    credentials: "include",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseOkBody(res);
  return data as TResponse;
}

export async function DELETE<TResponse = null>(
  path: string
): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "DELETE",
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseOkBody(res);
  return data as TResponse;
}

export type SseEvent = { event: string; data: string };

async function* parseSSE(
  stream: ReadableStream<Uint8Array>,
  signal?: AbortSignal
): AsyncGenerator<SseEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();

  let buf = "";
  let eventName = "message";
  let dataLines: string[] = [];

  const flush = () => {
    const evt: SseEvent = {
      event: eventName || "message",
      data: dataLines.join("\n"),
    };
    eventName = "message";
    dataLines = [];
    return evt;
  };

  while (true) {
    if (signal?.aborted) throw new DOMException("Aborted", "AbortError");

    const { value, done } = await reader.read();
    if (done) break;

    buf += decoder.decode(value, { stream: true });

    let lineEnd = buf.indexOf("\n");
    while (lineEnd !== -1) {
      let line = buf.slice(0, lineEnd);
      buf = buf.slice(lineEnd + 1);
      lineEnd = buf.indexOf("\n");

      if (line.endsWith("\r")) line = line.slice(0, -1);

      if (line === "") {
        if (dataLines.length > 0 || eventName !== "message") yield flush();
        continue;
      }

      if (line.startsWith("event:")) {
        eventName = line.slice("event:".length).trim() || "message";
        continue;
      }

      if (line.startsWith("data:")) {
        const d = line.slice("data:".length);
        dataLines.push(d.startsWith(" ") ? d.slice(1) : d);
      }
    }
  }

  if (dataLines.length > 0 || eventName !== "message") yield flush();
}

export async function* POST_STREAM<TBody extends object>(
  path: string,
  body: TBody,
  opts?: { signal?: AbortSignal }
): AsyncGenerator<SseEvent> {
  const res = await fetch(toUrl(path), {
    method: "POST",
    credentials: "include",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
      Pragma: "no-cache",
    },
    body: JSON.stringify(body),
    signal: opts?.signal,
  });

  if (!res.ok) {
    await throwApiError(res);
  }

  if (!res.body) {
    throw {
      status: 500,
      data: { detail: "Missing response body" },
    } satisfies ApiError;
  }

  yield* parseSSE(res.body, opts?.signal);
}
