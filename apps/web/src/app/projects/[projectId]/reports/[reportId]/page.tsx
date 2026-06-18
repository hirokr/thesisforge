"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle2, ClipboardCopy, Download, Play, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { DefenseQuestionsList } from "@/components/report/defense-questions-list";
import { PriorityFixList } from "@/components/report/priority-fix-list";
import { OverallScoreCard, ScoreBreakdownCards } from "@/components/report/score-cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getProject, getReport, trackReportEvent, type Report } from "@/lib/api";
import { cn } from "@/lib/utils";

type ToastState = {
  message: string;
  variant: "success" | "danger";
};

export default function FinalReportPage() {
  const params = useParams<{ projectId: string; reportId: string }>();
  const projectId = params.projectId;
  const reportId = params.reportId;
  const [report, setReport] = useState<Report | null>(null);
  const [projectTitle, setProjectTitle] = useState("thesis-project");
  const [isLoading, setIsLoading] = useState(true);
  const [isCopying, setIsCopying] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [toast, setToast] = useState<ToastState | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadReport() {
    setIsLoading(true);
    setError(null);
    setToast(null);

    try {
      const [reportResponse, projectResponse] = await Promise.all([getReport(reportId), getProject(projectId)]);
      if (reportResponse.project_id !== projectId) {
        throw new Error("This report does not belong to the selected project.");
      }
      setReport(reportResponse);
      setProjectTitle(projectResponse.title);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load report.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReport();
  }, [projectId, reportId]);

  async function copyReport() {
    if (!report) {
      return;
    }

    setIsCopying(true);
    try {
      await navigator.clipboard.writeText(getReportMarkdown(report));
      void trackReportEvent(report.id, "report_copied").catch(() => undefined);
      showToast("Report copied to clipboard.", "success");
    } catch {
      showToast("Copy failed.", "danger");
    } finally {
      setIsCopying(false);
    }
  }

  function downloadMarkdown() {
    if (!report) {
      return;
    }

    setIsDownloading(true);
    try {
      const blob = new Blob([getReportMarkdown(report)], { type: "text/markdown;charset=utf-8" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${slugify(projectTitle)}-${formatDateForFilename(report.created_at)}.md`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      showToast("Markdown report downloaded.", "success");
    } catch {
      showToast("Download failed.", "danger");
    } finally {
      setIsDownloading(false);
    }
  }

  function showToast(message: string, variant: ToastState["variant"]) {
    setToast({ message, variant });
    window.setTimeout(() => setToast(null), 3200);
  }

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
            <h1 className="text-2xl font-semibold text-foreground">Final thesis health report</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {report?.title ?? "Review the generated report, scores, fixes, and defense preparation notes."}
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            <Button asChild variant="outline" className="w-full sm:w-auto">
              <Link href={`/projects/${projectId}/review`}>
                <Play className="size-4" />
                Run review again
              </Link>
            </Button>
            <Button className="w-full sm:w-auto" onClick={() => void copyReport()} disabled={!report || isCopying}>
              <ClipboardCopy className="size-4" />
              Copy report
            </Button>
            <Button variant="outline" className="w-full sm:w-auto" onClick={downloadMarkdown} disabled={!report || isDownloading}>
              <Download className="size-4" />
              Download markdown
            </Button>
          </div>
        </div>

        {toast ? <ToastMessage toast={toast} /> : null}

        {isLoading ? (
          <ReportPageSkeleton />
        ) : error ? (
          <ReportState
            icon={<AlertCircle className="size-5" />}
            title="Report unavailable"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadReport()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : report ? (
          <>
            <section className="grid gap-4 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)]">
              <OverallScoreCard score={report.overall_score} createdAt={report.created_at} />
              <ScoreBreakdownCards scoreBreakdown={report.score_breakdown} />
            </section>

            <Card>
              <CardHeader>
                <CardTitle>Executive summary</CardTitle>
                <CardDescription>Top-level assessment generated by the report agent.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap text-sm leading-6 text-foreground">
                  {report.executive_summary || "No executive summary was included in this report."}
                </p>
              </CardContent>
            </Card>

            <section className="grid gap-4 xl:grid-cols-2">
              <PriorityFixList structuredReport={report.structured_report} />
              <DefenseQuestionsList structuredReport={report.structured_report} />
            </section>

            <Card>
              <CardHeader>
                <CardTitle>Markdown report</CardTitle>
                <CardDescription>Full generated report content.</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="max-h-[560px] max-w-full overflow-auto whitespace-pre-wrap break-words rounded-md border border-border bg-muted p-4 text-sm leading-6 text-foreground">
                  {report.content || "No markdown report content was included."}
                </pre>
              </CardContent>
            </Card>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function ReportPageSkeleton() {
  return (
    <div className="grid gap-6" aria-label="Loading final report">
      <section className="grid gap-4 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-28" />
            <Skeleton className="h-4 w-36" />
          </CardHeader>
          <CardContent className="grid place-items-center gap-4">
            <Skeleton className="size-32 rounded-full" />
            <Skeleton className="h-4 w-40" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-36" />
            <Skeleton className="h-4 w-56" />
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-44" />
          <Skeleton className="h-4 w-72" />
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent className="grid gap-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-44" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent className="grid gap-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-80" />
        </CardContent>
      </Card>
    </div>
  );
}

function ToastMessage({ toast }: { toast: ToastState }) {
  return (
    <div
      role="status"
      className={cn(
        "fixed right-4 top-4 z-50 flex max-w-sm items-center gap-3 rounded-md border bg-card p-4 text-sm shadow-lg",
        toast.variant === "danger" ? "border-danger/30 text-danger" : "border-success/30 text-success"
      )}
    >
      {toast.variant === "success" ? <CheckCircle2 className="size-5 shrink-0" /> : <AlertCircle className="size-5 shrink-0" />}
      <span>{toast.message}</span>
    </div>
  );
}

function ReportState({
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
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
        </div>
        {action}
      </CardContent>
    </Card>
  );
}

function getReportMarkdown(report: Report): string {
  if (report.content?.trim()) {
    return report.content;
  }

  const summary = report.executive_summary?.trim() || "No executive summary was included.";
  const score = report.overall_score === null ? "Unscored" : String(Math.round(report.overall_score));
  return `# ${report.title}\n\nOverall score: ${score}\n\n## Executive Summary\n\n${summary}\n`;
}

function slugify(value: string): string {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "thesis-project";
}

function formatDateForFilename(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "report";
  }
  return date.toISOString().slice(0, 10);
}
