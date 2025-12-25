const API_URL = process.env.API_URL;

export async function GET(path: string) {
  const res = await fetch(API_URL + path, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  const data = await res.json();

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

  const data = await res.json();

  if (!res.ok) {
    throw { status: res.status, data };
  }

  return data;
}
