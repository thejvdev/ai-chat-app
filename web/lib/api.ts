import type { ApiError } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export function toUrl(path: string): string {
  return `${API_URL}${path}`;
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

export async function throwApiError(res: Response): Promise<never> {
  const detail = await readErrorDetail(res);
  throw { status: res.status, data: { detail } } satisfies ApiError;
}

async function parseBody(res: Response): Promise<unknown> {
  if (res.status === 204 || res.status === 205) return null;

  const ct = res.headers.get("content-type")?.toLowerCase() ?? "";
  if (ct.includes("json")) {
    return (await res.json()) as unknown;
  }

  return (await res.text()) as unknown;
}

export async function GET<TResponse>(path: string): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseBody(res);
  return data as TResponse;
}

export async function POST<TResponse, TBody>(
  path: string,
  body?: TBody
): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "POST",
    credentials: "include",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseBody(res);
  return data as TResponse;
}

export async function DELETE<TResponse>(path: string): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "DELETE",
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseBody(res);
  return data as TResponse;
}

export async function PATCH<TResponse, TBody>(
  path: string,
  body?: TBody
): Promise<TResponse> {
  const res = await fetch(toUrl(path), {
    method: "PATCH",
    credentials: "include",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) await throwApiError(res);

  const data = await parseBody(res);
  return data as TResponse;
}
