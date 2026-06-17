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

export type DemoProjectResult = {
  project: Project;
  document_count: number;
  reference_count: number;
};

export type UpdateProjectPayload = Partial<CreateProjectPayload> & {
  status?: string | null;
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
  raw_text: string | null;
  created_at: string;
  updated_at: string;
  parse_status: string;
  parse_metadata: Record<string, unknown> | null;
};

export type CreateTextDocumentPayload = {
  document_type: string;
  title: string;
  raw_text: string;
};

export type TextDocumentResult = {
  id: string;
  project_id: string;
  document_type: string;
  title: string;
  parse_status: string;
  word_count: number;
  chunk_count: number;
};

export type AnalysisRun = {
  id: string;
  project_id: string;
  status: string;
  summary: string | null;
  overall_score: number | null;
  current_agent: string | null;
  progress_percentage: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type StartAnalysisRunPayload = {
  include_results_agent?: boolean;
};

export type AnalysisRunStatus = Pick<
  AnalysisRun,
  "id" | "project_id" | "status" | "current_agent" | "progress_percentage" | "summary" | "overall_score" | "started_at" | "completed_at"
>;

export type AgentMessage = {
  id: string;
  analysis_run_id: string;
  project_id: string | null;
  from_agent_id: string | null;
  from_agent_name: string | null;
  from_agent_slug: string | null;
  to_agent_id: string | null;
  to_agent_name: string | null;
  to_agent_slug: string | null;
  message_type: string;
  task: string | null;
  summary: string | null;
  content: string;
  status: string;
  band_message_id: string | null;
  created_at: string;
};

export type Report = {
  id: string;
  project_id: string;
  analysis_run_id: string | null;
  title: string;
  status: string;
  overall_score: number | null;
  score_breakdown: Record<string, unknown> | null;
  executive_summary: string | null;
  content: string | null;
  structured_report: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type ActionTaskStatus = "open" | "in_progress" | "completed" | "dismissed";

export type ActionTask = {
  id: string;
  project_id: string;
  report_id: string | null;
  finding_id: string | null;
  title: string;
  description: string | null;
  category: string | null;
  priority: string;
  status: ActionTaskStatus;
  due_at: string | null;
  created_at: string;
  updated_at: string;
};

export type FeedbackSource = "meeting" | "email" | "document_comment" | "manual";

export type SupervisorFeedback = {
  id: string;
  project_id: string;
  feedback_text: string;
  source: string;
  feedback_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type CreateSupervisorFeedbackPayload = {
  feedback_text: string;
  source?: FeedbackSource;
  feedback_date?: string | null;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string
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

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${readPublicEnv("NEXT_PUBLIC_API_BASE_URL")}${path}`, {
    ...init,
    headers
  });

  if (!response.ok) {
    const error = await getErrorPayload(response);
    throw new ApiError(error.message, response.status, error.code);
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

export function loadDemoProject(): Promise<DemoProjectResult> {
  return apiRequest<DemoProjectResult>("/demo/project", {
    method: "POST"
  });
}

export function getProject(projectId: string): Promise<Project> {
  return apiRequest<Project>(`/projects/${projectId}`);
}

export function updateProject(projectId: string, payload: UpdateProjectPayload): Promise<Project> {
  return apiRequest<Project>(`/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function listProjectDocuments(projectId: string): Promise<Document[]> {
  return apiRequest<Document[]>(`/projects/${projectId}/documents`);
}

export function createTextDocument(projectId: string, payload: CreateTextDocumentPayload): Promise<TextDocumentResult> {
  return apiRequest<TextDocumentResult>(`/projects/${projectId}/documents/text`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function uploadProjectDocument(projectId: string, documentType: string, file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("file", file);

  return apiRequest<Document>(`/projects/${projectId}/documents`, {
    method: "POST",
    body: formData
  });
}

export function startAnalysisRun(projectId: string, payload: StartAnalysisRunPayload = {}): Promise<AnalysisRun> {
  return apiRequest<AnalysisRun>(`/projects/${projectId}/analysis-runs`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getAnalysisRunStatus(runId: string): Promise<AnalysisRunStatus> {
  return apiRequest<AnalysisRunStatus>(`/analysis-runs/${runId}/status`);
}

export function listAgentMessages(runId: string): Promise<AgentMessage[]> {
  return apiRequest<AgentMessage[]>(`/analysis-runs/${runId}/agent-messages`);
}

export function listProjectReports(projectId: string): Promise<Report[]> {
  return apiRequest<Report[]>(`/projects/${projectId}/reports`);
}

export function getReport(reportId: string): Promise<Report> {
  return apiRequest<Report>(`/reports/${reportId}`);
}

export function listProjectTasks(projectId: string): Promise<ActionTask[]> {
  return apiRequest<ActionTask[]>(`/projects/${projectId}/tasks`);
}

export function updateTaskStatus(taskId: string, status: ActionTaskStatus): Promise<ActionTask> {
  return apiRequest<ActionTask>(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
}

export function listProjectFeedback(projectId: string): Promise<SupervisorFeedback[]> {
  return apiRequest<SupervisorFeedback[]>(`/projects/${projectId}/feedback`);
}

export function createProjectFeedback(projectId: string, payload: CreateSupervisorFeedbackPayload): Promise<SupervisorFeedback> {
  return apiRequest<SupervisorFeedback>(`/projects/${projectId}/feedback`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function deleteTask(taskId: string): Promise<void> {
  return apiRequest<void>(`/tasks/${taskId}`, {
    method: "DELETE"
  });
}

async function getErrorPayload(response: Response): Promise<{ message: string; code?: string }> {
  try {
    const body = (await response.json()) as { code?: unknown; detail?: unknown; message?: unknown };
    if (typeof body.message === "string") {
      return {
        message: body.message,
        code: typeof body.code === "string" ? body.code : undefined
      };
    }
    if (typeof body.detail === "string") {
      return { message: body.detail };
    }
  } catch {
    return { message: "Request failed." };
  }

  return { message: "Request failed." };
}
