import { getAccessToken } from "@/lib/auth";
import { readPublicEnv } from "@/lib/env";

export type Project = {
  id: string;
  owner_id: string;
  title: string;
  research_area: string | null;
  thesis_stage: string | null;
  status: string;
  latest_score: number | null;
  abstract: string | null;
  problem_statement: string | null;
  research_gap: string | null;
  objectives: string | null;
  methodology_summary: string | null;
  dataset_summary: string | null;
  results_summary: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateProjectPayload = {
  title: string;
  research_area?: string | null;
  thesis_stage?: string | null;
  problem_statement?: string | null;
  research_gap?: string | null;
  objectives?: string | null;
  methodology_summary?: string | null;
  dataset_summary?: string | null;
  results_summary?: string | null;
  abstract?: string | null;
};

export type Document = {
  id: string;
  project_id: string;
  filename: string;
  storage_path: string | null;
  content_type: string | null;
  document_type: string;
  size_bytes: number | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();

  if (!token) {
    throw new ApiError("You need to sign in again.", 401);
  }

  const response = await fetch(`${readPublicEnv("NEXT_PUBLIC_API_BASE_URL")}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...init.headers
    }
  });

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function listProjects(): Promise<Project[]> {
  return apiRequest<Project[]>("/projects");
}

export function createProject(payload: CreateProjectPayload): Promise<Project> {
  return apiRequest<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return apiRequest<Project>(`/projects/${projectId}`);
}

export function listProjectDocuments(projectId: string): Promise<Document[]> {
  return apiRequest<Document[]>(`/projects/${projectId}/documents`);
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    return "Request failed.";
  }

  return "Request failed.";
}
