const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function parseBody(res: Response) {
  if (res.status === 204 || res.status === 205) return null;

  const ct = res.headers.get("content-type")?.toLowerCase() ?? "";
  if (ct.includes("json")) return await res.json();

  return await res.text();
}

export async function GET(path: string) {
  const res = await fetch(API_URL + path, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  const data = await parseBody(res);

  if (!res.ok) {
    throw { status: res.status, data };
  }

  return data;
}

export async function POST(path: string, body?: object | undefined) {
  const res = await fetch(API_URL + path, {
    method: "POST",
    credentials: "include",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const data = await parseBody(res);

  if (!res.ok) {
    throw { status: res.status, data };
  }

  return data;
}
