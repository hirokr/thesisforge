"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle2, Clock3, RefreshCw, ScrollText, Timer, XCircle } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getAnalysisRunStatus,
  getProject,
  type AnalysisRunStatus,
  type Project
} from "@/lib/api";
import { cn } from "@/lib/utils";

const POLL_INTERVAL_MS = 4000;
const terminalStatuses = new Set(["completed", "failed", "partial"]);

export default function AnalysisRunProgressPage() {
  const params = useParams<{ projectId: string; runId: string }>();
  const projectId = params.projectId;
  const runId = params.runId;
  const [project, setProject] = useState<Project | null>(null);
  const [runStatus, setRunStatus] = useState<AnalysisRunStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isTerminal = runStatus ? terminalStatuses.has(runStatus.status) : false;
  const progress = clampProgress(runStatus?.progress_percentage ?? 0);

  async function loadRunStatus({ initial = false }: { initial?: boolean } = {}) {
    if (initial) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError(null);

    try {
      const [projectResponse, statusResponse] = await Promise.all([
        project ? Promise.resolve(project) : getProject(projectId),
        getAnalysisRunStatus(runId)
      ]);
      setProject(projectResponse);
      setRunStatus(statusResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load analysis run.");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    void loadRunStatus({ initial: true });
  }, [projectId, runId]);

  useEffect(() => {
    if (!runStatus || isTerminal || error) {
      return;
    }

    const pollId = window.setInterval(() => {
      void loadRunStatus();
    }, POLL_INTERVAL_MS);

    return () => window.clearInterval(pollId);
  }, [runStatus?.id, runStatus?.status, error]);

  const statusTone = useMemo(() => getStatusTone(runStatus?.status), [runStatus?.status]);

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Button asChild variant="ghost" className="-ml-3 mb-2">
              <Link href={`/projects/${projectId}`}>
                <ArrowLeft className="size-4" />
                Project overview
              </Link>
            </Button>
            <h1 className="text-2xl font-semibold text-foreground">Analysis run progress</h1>
            <p className="mt-2 text-sm text-muted-foreground">{project?.title ?? "Tracking thesis review status."}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {runStatus ? <Badge variant={statusTone.badge}>{formatStatus(runStatus.status)}</Badge> : null}
            <Badge variant="outline">{progress}% complete</Badge>
          </div>
        </div>

        {isLoading ? (
          <RunState icon={<RefreshCw className="size-5 animate-spin" />} title="Loading run" description="Fetching the latest analysis status." />
        ) : error ? (
          <RunState
            icon={<AlertCircle className="size-5" />}
            title="Run unavailable"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadRunStatus({ initial: true })}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : runStatus ? (
          <>
            <Card>
              <CardHeader className="gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <CardTitle>Current status</CardTitle>
                  <CardDescription>
                    {isTerminal ? "Polling has stopped because the run reached a final state." : "This page refreshes automatically every 4 seconds."}
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={() => void loadRunStatus()} disabled={isRefreshing}>
                  <RefreshCw className={cn("size-4", isRefreshing && "animate-spin")} />
                  Refresh
                </Button>
              </CardHeader>
              <CardContent className="grid gap-5">
                <div className="h-3 overflow-hidden rounded-full bg-muted">
                  <div
                    className={cn("h-full rounded-full transition-all", statusTone.progress)}
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  <Metric icon={<Timer className="size-4" />} label="Progress" value={`${progress}%`} />
                  <Metric icon={<RefreshCw className="size-4" />} label="Current agent" value={formatAgent(runStatus.current_agent)} />
                  <Metric icon={<Clock3 className="size-4" />} label="Started" value={formatDateTime(runStatus.started_at)} />
                </div>

                {runStatus.status === "failed" ? (
                  <div className="flex gap-3 rounded-md border border-danger/30 bg-danger/5 p-4">
                    <XCircle className="mt-0.5 size-5 shrink-0 text-danger" />
                    <div>
                      <h2 className="text-sm font-medium text-danger">Analysis failed</h2>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {runStatus.summary || "The worker could not complete this review. Refresh after checking the worker logs."}
                      </p>
                    </div>
                  </div>
                ) : null}

                {runStatus.status === "completed" ? (
                  <div className="flex flex-col gap-4 rounded-md border border-success/30 bg-success/5 p-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex gap-3">
                      <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" />
                      <div>
                        <h2 className="text-sm font-medium text-foreground">Review completed</h2>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {runStatus.overall_score === null ? "The final report is ready to review." : `Overall score: ${Math.round(runStatus.overall_score)}%.`}
                        </p>
                      </div>
                    </div>
                    <Button asChild>
                      <Link href="/reports">
                        <ScrollText className="size-4" />
                        View report
                      </Link>
                    </Button>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <div className="mb-3 flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-xs font-medium uppercase tracking-normal">{label}</span>
      </div>
      <p className="break-words text-sm font-semibold text-foreground">{value}</p>
    </div>
  );
}

function RunState({
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

function getStatusTone(status: string | undefined): {
  badge: "default" | "secondary" | "success" | "warning" | "danger" | "outline";
  progress: string;
} {
  switch (status) {
    case "completed":
      return { badge: "success", progress: "bg-success" };
    case "failed":
      return { badge: "danger", progress: "bg-danger" };
    case "partial":
      return { badge: "warning", progress: "bg-warning" };
    case "running":
      return { badge: "default", progress: "bg-primary" };
    case "queued":
      return { badge: "secondary", progress: "bg-secondary-foreground" };
    default:
      return { badge: "outline", progress: "bg-muted-foreground" };
  }
}

function clampProgress(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function formatStatus(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatAgent(agent: string | null): string {
  if (!agent) {
    return "Waiting";
  }

  return agent
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatDateTime(value: string | null): string {
  if (!value) {
    return "Not started";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
