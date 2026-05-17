import type { DailyDigest } from "@/types/news";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function fetchNews(date?: string): Promise<DailyDigest | null> {
  const url = date
    ? `${API_BASE}/api/news?date=${date}`
    : `${API_BASE}/api/news`;

  const res = await fetch(url);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json() as Promise<DailyDigest>;
}

export async function fetchAvailableDates(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/news/dates`);
  if (!res.ok) return [];
  const data = (await res.json()) as { dates?: string[] };
  return data.dates ?? [];
}

export async function subscribeEmail(email: string): Promise<{ status: number; message: string }> {
  const res = await fetch(`${API_BASE}/api/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const data = (await res.json()) as { message?: string; error?: string };
  return { status: res.status, message: data.message ?? data.error ?? "" };
}
