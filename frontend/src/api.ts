import type { DashboardResponse, ParseResponse, UserAssumptions } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE}/api/v1/dashboard/overview`);
  return parseJson<DashboardResponse>(response);
}

export async function uploadSyllabus(file: File): Promise<ParseResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/v1/syllabus/parse`, {
    method: "POST",
    body: formData,
  });

  return parseJson<ParseResponse>(response);
}

export async function putUserAssumptions(assumptions: UserAssumptions): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/api/v1/user/assumptions`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(assumptions),
  });
  return parseJson<{ status: string }>(response);
}

export function getGoogleOAuthUrl(): string {
  return `${API_BASE}/api/v1/auth/google/login`;
}

export async function syncGoogleCalendar(): Promise<{ status: string, blocks_synced: number, mode: string }> {
  const response = await fetch(`${API_BASE}/api/v1/user/sync-calendar`);
  return parseJson<{ status: string, blocks_synced: number, mode: string }>(response);
}

export async function addFriend(friendName: string, homeZone: string): Promise<{ status: string, friend_id: string }> {
  const response = await fetch(`${API_BASE}/api/v1/friends`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ friend_name: friendName, home_zone: homeZone }),
  });
  return parseJson<{ status: string, friend_id: string }>(response);
}
