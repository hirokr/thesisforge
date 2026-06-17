"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle2, FileUp, MessageSquareText, Pencil, Play, RefreshCw, Save, ScrollText, Send, X } from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { ActionTaskList } from "@/components/tasks/action-task-list";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  type ActionTask,
  type ActionTaskStatus,
  createProjectFeedback,
  type FeedbackSource,
  getProject,
  listProjectFeedback,
  listProjectTasks,
  listProjectDocuments,
  updateProject,
  updateTaskStatus,
  type Document,
  type Project,
  type SupervisorFeedback,
  type UpdateProjectPayload
} from "@/lib/api";

type ProjectEditForm = {
  research_area: string;
  thesis_stage: string;
  problem_statement: string;
  research_gap: string;
  objectives: string;
  methodology_summary: string;
  dataset_summary: string;
  results_summary: string;
};

const editableFields: Array<{
  name: keyof ProjectEditForm;
  label: string;
  multiline?: boolean;
}> = [
  { name: "research_area", label: "Research area" },
  { name: "thesis_stage", label: "Thesis stage" },
  { name: "problem_statement", label: "Problem statement", multiline: true },
  { name: "research_gap", label: "Research gap", multiline: true },
  { name: "objectives", label: "Objectives", multiline: true },
  { name: "methodology_summary", label: "Methodology summary", multiline: true },
  { name: "dataset_summary", label: "Dataset summary", multiline: true },
  { name: "results_summary", label: "Results summary", multiline: true }
];

const feedbackSources: Array<{ value: FeedbackSource; label: string }> = [
  { value: "meeting", label: "Meeting" },
  { value: "email", label: "Email" },
  { value: "document_comment", label: "Document comment" },
  { value: "manual", label: "Manual" }
];

export default function ProjectOverviewPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params.projectId;
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [tasks, setTasks] = useState<ActionTask[]>([]);
  const [feedback, setFeedback] = useState<SupervisorFeedback[]>([]);
  const [editForm, setEditForm] = useState<ProjectEditForm>(() => emptyProjectEditForm());
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSource, setFeedbackSource] = useState<FeedbackSource>("manual");
  const [feedbackDate, setFeedbackDate] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);
  const [isUpdatingTask, setIsUpdatingTask] = useState(false);
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [showSuccessToast, setShowSuccessToast] = useState(false);

  async function loadProject() {
    setIsLoading(true);
    setError(null);
    setSaveError(null);
    setTaskError(null);

    try {
      const [projectResponse, documentsResponse, tasksResponse, feedbackResponse] = await Promise.all([
        getProject(projectId),
        listProjectDocuments(projectId),
        listProjectTasks(projectId),
        listProjectFeedback(projectId)
      ]);
      setProject(projectResponse);
      setEditForm(projectToEditForm(projectResponse));
      setDocuments(documentsResponse);
      setTasks(tasksResponse);
      setFeedback(feedbackResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load project.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadProject();
  }, [projectId]);

  const latestDocument = useMemo(() => documents[0] ?? null, [documents]);

  function startEditing() {
    if (!project) {
      return;
    }

    setEditForm(projectToEditForm(project));
    setSaveError(null);
    setShowSuccessToast(false);
    setIsEditing(true);
  }

  function cancelEditing() {
    if (project) {
      setEditForm(projectToEditForm(project));
    }

    setSaveError(null);
    setIsEditing(false);
  }

  async function saveProjectDetails() {
    setIsSaving(true);
    setSaveError(null);
    setShowSuccessToast(false);

    try {
      const updatedProject = await updateProject(projectId, editFormToPayload(editForm));
      setProject(updatedProject);
      setEditForm(projectToEditForm(updatedProject));
      setIsEditing(false);
      setShowSuccessToast(true);
      window.setTimeout(() => setShowSuccessToast(false), 3500);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Could not save project details.");
    } finally {
      setIsSaving(false);
    }
  }

  async function updateActionTaskStatus(taskId: string, status: ActionTaskStatus) {
    setIsUpdatingTask(true);
    setUpdatingTaskId(taskId);
    setTaskError(null);

    try {
      const updatedTask = await updateTaskStatus(taskId, status);
      setTasks((currentTasks) => currentTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task)));
    } catch (err) {
      setTaskError(err instanceof Error ? err.message : "Could not update task.");
    } finally {
      setIsUpdatingTask(false);
      setUpdatingTaskId(null);
    }
  }

  async function submitSupervisorFeedback(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedbackError(null);

    if (!feedbackText.trim()) {
      setFeedbackError("Enter supervisor feedback before saving.");
      return;
    }

    setIsSavingFeedback(true);
    try {
      const createdFeedback = await createProjectFeedback(projectId, {
        feedback_text: feedbackText.trim(),
        source: feedbackSource,
        feedback_date: feedbackDate ? `${feedbackDate}T00:00:00Z` : null
      });
      setFeedback((currentFeedback) => [createdFeedback, ...currentFeedback]);
      setFeedbackText("");
      setFeedbackSource("manual");
      setFeedbackDate("");
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : "Could not save supervisor feedback.");
    } finally {
      setIsSavingFeedback(false);
    }
  }

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        {showSuccessToast ? (
          <div className="fixed right-4 top-4 z-50 flex max-w-sm items-center gap-3 rounded-md border border-success/30 bg-card px-4 py-3 text-sm shadow-lg">
            <CheckCircle2 className="size-5 shrink-0 text-success" />
            <div>
              <p className="font-medium text-foreground">Project details saved</p>
              <p className="text-muted-foreground">The thesis metadata is up to date.</p>
            </div>
          </div>
        ) : null}

        <Button asChild variant="ghost" className="w-fit -ml-3">
          <Link href="/dashboard">
            <ArrowLeft className="size-4" />
            Dashboard
          </Link>
        </Button>

        {isLoading ? (
          <ProjectState icon={<RefreshCw className="size-5 animate-spin" />} title="Loading project" description="Fetching thesis metadata and documents." />
        ) : error || !project ? (
          <ProjectState
            icon={<AlertCircle className="size-5" />}
            title="Project unavailable"
            description={error || "This project could not be found."}
            action={
              <Button variant="outline" onClick={() => void loadProject()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : (
          <>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge variant="secondary">{project.status}</Badge>
                  <Badge variant="outline">{project.thesis_stage || "Stage not set"}</Badge>
                </div>
                <h1 className="break-words text-2xl font-semibold text-foreground">{project.title}</h1>
                <p className="mt-2 text-sm text-muted-foreground">{project.research_area || "Research area not set"}</p>
              </div>
              <div className="flex flex-col gap-2 sm:flex-row">
                <Button asChild variant="outline">
                  <Link href={`/projects/${project.id}/upload`}>
                    <FileUp className="size-4" />
                    Upload documents
                  </Link>
                </Button>
                <Button asChild>
                  <Link href={`/projects/${project.id}/review`}>
                    <Play className="size-4" />
                    Run thesis review
                  </Link>
                </Button>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <SummaryCard label="Documents" value={String(documents.length)} detail={latestDocument ? `Latest: ${latestDocument.filename}` : "No uploads yet"} />
              <SummaryCard label="Latest analysis" value="Not run" detail="Analysis workflow is not queued." />
              <SummaryCard
                label="Latest report"
                value={project.latest_score === null ? "No score" : `${Math.round(project.latest_score)}%`}
                detail={project.latest_score === null ? "No generated report yet." : "Report score available."}
              />
            </div>

            <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
              <Card>
                <CardHeader className="gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <CardTitle>Thesis metadata</CardTitle>
                    <CardDescription>Core context for the review agents.</CardDescription>
                  </div>
                  {isEditing ? (
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={cancelEditing} disabled={isSaving}>
                        <X className="size-4" />
                        Cancel
                      </Button>
                      <Button onClick={() => void saveProjectDetails()} disabled={isSaving}>
                        {isSaving ? <RefreshCw className="size-4 animate-spin" /> : <Save className="size-4" />}
                        Save
                      </Button>
                    </div>
                  ) : (
                    <Button variant="outline" onClick={startEditing}>
                      <Pencil className="size-4" />
                      Edit details
                    </Button>
                  )}
                </CardHeader>
                <CardContent className="grid gap-4">
                  {saveError ? (
                    <div className="rounded-md border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
                      {saveError}
                    </div>
                  ) : null}

                  {isEditing ? (
                    <FieldGroup>
                      {editableFields.map((field) => (
                        <Field key={field.name}>
                          <FieldLabel htmlFor={field.name}>{field.label}</FieldLabel>
                          {field.multiline ? (
                            <textarea
                              id={field.name}
                              value={editForm[field.name]}
                              onChange={(event) =>
                                setEditForm((current) => ({
                                  ...current,
                                  [field.name]: event.target.value
                                }))
                              }
                              rows={field.name === "objectives" ? 5 : 4}
                              className={cn(
                                "min-h-24 w-full rounded-md border border-input bg-card px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                              )}
                            />
                          ) : (
                            <Input
                              id={field.name}
                              value={editForm[field.name]}
                              onChange={(event) =>
                                setEditForm((current) => ({
                                  ...current,
                                  [field.name]: event.target.value
                                }))
                              }
                            />
                          )}
                        </Field>
                      ))}
                    </FieldGroup>
                  ) : (
                    <>
                      <MetadataBlock label="Problem statement" value={project.problem_statement} />
                      <MetadataBlock label="Research gap" value={project.research_gap} />
                      <MetadataBlock label="Objectives" value={project.objectives} />
                      <MetadataBlock label="Methodology" value={project.methodology_summary} />
                      <MetadataBlock label="Dataset" value={project.dataset_summary} />
                      <MetadataBlock label="Results" value={project.results_summary} />
                    </>
                  )}
                </CardContent>
              </Card>

              <div className="grid gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Next actions</CardTitle>
                    <CardDescription>Continue the project workflow.</CardDescription>
                  </CardHeader>
                  <CardContent className="grid gap-3">
                    <Button asChild variant="outline" className="justify-start">
                      <Link href={`/projects/${project.id}/upload`}>
                        <FileUp className="size-4" />
                        Add thesis materials
                      </Link>
                    </Button>
                    <Button asChild variant="outline" className="justify-start">
                      <Link href={`/projects/${project.id}/review`}>
                        <Play className="size-4" />
                        Run review
                      </Link>
                    </Button>
                    <Button asChild variant="outline" className="justify-start" aria-disabled={project.latest_score === null}>
                      <Link href="/reports">
                        <ScrollText className="size-4" />
                        View latest report
                      </Link>
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Supervisor feedback</CardTitle>
                    <CardDescription>Notes from meetings, email, or document comments.</CardDescription>
                  </CardHeader>
                  <CardContent className="grid gap-4">
                    <form className="grid gap-4" onSubmit={submitSupervisorFeedback}>
                      <Field>
                        <FieldLabel htmlFor="feedbackText">Feedback</FieldLabel>
                        <textarea
                          id="feedbackText"
                          value={feedbackText}
                          onChange={(event) => setFeedbackText(event.target.value)}
                          rows={5}
                          className={cn(
                            "w-full rounded-md border border-input bg-card px-3 py-2 text-sm shadow-sm transition-colors",
                            "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                          )}
                        />
                        <FieldError>{feedbackError}</FieldError>
                      </Field>
                      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                        <Field>
                          <FieldLabel htmlFor="feedbackSource">Source</FieldLabel>
                          <select
                            id="feedbackSource"
                            value={feedbackSource}
                            onChange={(event) => setFeedbackSource(event.target.value as FeedbackSource)}
                            className="h-10 w-full rounded-md border border-input bg-card px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                          >
                            {feedbackSources.map((source) => (
                              <option key={source.value} value={source.value}>
                                {source.label}
                              </option>
                            ))}
                          </select>
                        </Field>
                        <Field>
                          <FieldLabel htmlFor="feedbackDate">Date</FieldLabel>
                          <Input id="feedbackDate" type="date" value={feedbackDate} onChange={(event) => setFeedbackDate(event.target.value)} />
                        </Field>
                      </div>
                      <Button type="submit" disabled={isSavingFeedback}>
                        {isSavingFeedback ? <RefreshCw className="size-4 animate-spin" /> : <Send className="size-4" />}
                        {isSavingFeedback ? "Saving" : "Save feedback"}
                      </Button>
                    </form>

                    {feedback.length === 0 ? (
                      <div className="rounded-md border border-dashed border-border bg-background px-4 py-6 text-center">
                        <MessageSquareText className="mx-auto size-6 text-muted-foreground" />
                        <p className="mt-3 text-sm font-medium text-foreground">No feedback yet</p>
                      </div>
                    ) : (
                      <div className="grid gap-3">
                        {feedback.map((item) => (
                          <FeedbackRow key={item.id} feedback={item} />
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            <ActionTaskList
              tasks={tasks}
              isUpdating={isUpdatingTask}
              updatingTaskId={updatingTaskId}
              error={taskError}
              onStatusChange={(taskId, status) => void updateActionTaskStatus(taskId, status)}
            />
          </>
        )}
      </div>
    </AppShell>
  );
}

function ProjectState({
  icon,
  title,
  description,
  action
}: {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
        <div className="flex size-10 items-center justify-center rounded-md bg-primary-soft text-primary">{icon}</div>
        <div>
          <h1 className="text-base font-semibold text-foreground">{title}</h1>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
        </div>
        {action}
      </CardContent>
    </Card>
  );
}

function SummaryCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{detail}</p>
      </CardContent>
    </Card>
  );
}

function MetadataBlock({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <h2 className="text-sm font-medium text-foreground">{label}</h2>
      <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{value || "Not provided yet."}</p>
    </div>
  );
}

function FeedbackRow({ feedback }: { feedback: SupervisorFeedback }) {
  return (
    <article className="rounded-md border border-border bg-background p-3">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="outline">{formatFeedbackSource(feedback.source)}</Badge>
        {feedback.feedback_date ? <span className="text-xs text-muted-foreground">{formatDate(feedback.feedback_date)}</span> : null}
      </div>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{feedback.feedback_text}</p>
    </article>
  );
}

function emptyProjectEditForm(): ProjectEditForm {
  return {
    research_area: "",
    thesis_stage: "",
    problem_statement: "",
    research_gap: "",
    objectives: "",
    methodology_summary: "",
    dataset_summary: "",
    results_summary: ""
  };
}

function projectToEditForm(project: Project): ProjectEditForm {
  return {
    research_area: project.research_area ?? "",
    thesis_stage: project.thesis_stage ?? "",
    problem_statement: project.problem_statement ?? "",
    research_gap: project.research_gap ?? "",
    objectives: project.objectives ?? "",
    methodology_summary: project.methodology_summary ?? "",
    dataset_summary: project.dataset_summary ?? "",
    results_summary: project.results_summary ?? ""
  };
}

function editFormToPayload(form: ProjectEditForm): UpdateProjectPayload {
  return Object.fromEntries(
    Object.entries(form).map(([key, value]) => [key, value.trim() === "" ? null : value.trim()])
  ) as UpdateProjectPayload;
}

function formatFeedbackSource(source: string): string {
  return feedbackSources.find((item) => item.value === source)?.label ?? source.replaceAll("_", " ");
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString();
}
