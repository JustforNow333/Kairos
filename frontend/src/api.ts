import type { DashboardResponse, ParseResponse } from "./types";

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
