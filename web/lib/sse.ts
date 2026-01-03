import type { SseEvent, ApiError } from "@/types/api";
import { toUrl, throwApiError } from "@/lib/api";

async function* parseSse(
  stream: ReadableStream<Uint8Array>,
  signal: AbortSignal
): AsyncGenerator<SseEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  const empty = new Uint8Array();

  let buf = "";

  try {
    while (true) {
      if (signal.aborted) throw new DOMException("Aborted", "AbortError");

      const { value, done } = await reader.read();

      buf += decoder.decode(value ?? empty, { stream: !done });

      let idx: number;
      while ((idx = buf.indexOf("\n\n")) !== -1) {
        const raw = buf.slice(0, idx);
        buf = buf.slice(idx + 2);

        let event = "";
        let data = "";

        for (let line of raw.split("\n")) {
          if (!line) continue;
          if (line.endsWith("\r")) line = line.slice(0, -1);

          if (line.startsWith("event:")) {
            event = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            data = line.slice(5).trimStart();
          }
        }

        if (!event) continue;

        yield { event, data };
      }

      if (done) break;
    }
  } finally {
    reader.releaseLock();
  }
}

export async function* POST_SSE<TBody>(
  path: string,
  body: TBody,
  signal: AbortSignal
): AsyncGenerator<SseEvent> {
  const res = await fetch(toUrl(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
    credentials: "include",
    signal,
  });

  if (!res.ok) await throwApiError(res);

  if (!res.body) {
    throw {
      status: 500,
      data: { detail: "Missing response body" },
    } satisfies ApiError;
  }

  yield* parseSse(res.body, signal);
}
