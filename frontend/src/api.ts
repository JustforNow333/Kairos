import type { DashboardResponse, ParseResponse, UserAssumptions } from "./types";
import {
  addMockFriend,
  fetchMockDashboard,
  getMockGoogleOAuthUrl,
  putMockUserAssumptions,
  syncMockGoogleCalendar,
  uploadMockSyllabus,
} from "./mockApi";

const API_BASE =
  (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, "");
const USE_MOCK_API =
  process.env.NEXT_PUBLIC_USE_MOCK_API === "1" ||
  process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  if (USE_MOCK_API) {
    return fetchMockDashboard();
  }
  const response = await fetch(`${API_BASE}/api/v1/dashboard/overview`);
  return parseJson<DashboardResponse>(response);
}

export async function uploadSyllabus(file: File): Promise<ParseResponse> {
  if (USE_MOCK_API) {
    return uploadMockSyllabus(file);
  }
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/v1/syllabus/parse`, {
    method: "POST",
    body: formData,
  });

  return parseJson<ParseResponse>(response);
}

export async function putUserAssumptions(assumptions: UserAssumptions): Promise<{ status: string }> {
  if (USE_MOCK_API) {
    return putMockUserAssumptions(assumptions);
  }
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
  if (USE_MOCK_API) {
    return getMockGoogleOAuthUrl();
  }
  return `${API_BASE}/api/v1/auth/google/login`;
}

export async function syncGoogleCalendar(): Promise<{ status: string, blocks_synced: number, mode: string }> {
  if (USE_MOCK_API) {
    return syncMockGoogleCalendar();
  }
  const response = await fetch(`${API_BASE}/api/v1/user/sync-calendar`);
  return parseJson<{ status: string, blocks_synced: number, mode: string }>(response);
}

export async function addFriend(friendName: string, homeZone: string): Promise<{ status: string, friend_id: string }> {
  if (USE_MOCK_API) {
    return addMockFriend(friendName, homeZone);
  }
  const response = await fetch(`${API_BASE}/api/v1/friends`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ friend_name: friendName, home_zone: homeZone }),
  });
  return parseJson<{ status: string, friend_id: string }>(response);
}
