"use client";

import Link from "next/link";
import { AlertCircle, FileText, FolderOpen, LayoutDashboard, RefreshCw, ScrollText } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { listProjectReports, listProjects, type Project, type Report } from "@/lib/api";
import { friendlyErrorMessage } from "@/lib/errors";

type ReportIndexItem = {
  report: Report;
  project: Project;
};

export default function ReportsPage() {
  const [items, setItems] = useState<ReportIndexItem[]>([]);
  const [projectCount, setProjectCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadReports() {
    setIsLoading(true);
    setError(null);

    try {
      const projects = await listProjects();
      const reportGroups = await Promise.all(
        projects.map(async (project) => {
          const reports = await listProjectReports(project.id);
          return reports.map((report) => ({ report, project }));
        })
      );
      const nextItems = reportGroups
        .flat()
        .sort((left, right) => new Date(right.report.created_at).getTime() - new Date(left.report.created_at).getTime());
      setItems(nextItems);
      setProjectCount(projects.length);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReports();
  }, []);

  const completedCount = useMemo(
    () => items.filter((item) => item.report.status === "completed").length,
    [items]
  );

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Reports</h1>
            <p className="mt-2 text-sm text-muted-foreground">Review generated thesis health reports across your projects.</p>
          </div>
          <Button variant="outline" className="w-full sm:w-auto" onClick={() => void loadReports()} disabled={isLoading}>
            <RefreshCw className={isLoading ? "size-4 animate-spin" : "size-4"} />
            Refresh
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <SummaryCard label="Reports" value={String(items.length)} detail="Generated reviews" />
          <SummaryCard label="Completed" value={String(completedCount)} detail="Ready for demo review" />
          <SummaryCard label="Projects" value={String(projectCount)} detail="Checked for reports" />
        </div>

        {isLoading ? (
          <ReportsSkeleton />
        ) : error ? (
          <ReportsState
            icon={<AlertCircle className="size-5" />}
            title="Could not load reports"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadReports()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : items.length === 0 ? (
          <ReportsState
            icon={<FileText className="size-5" />}
            title="No reports yet"
            description="Run a thesis review from a project to generate scores, priority fixes, and defense questions."
            action={
              <div className="flex w-full flex-col justify-center gap-2 sm:w-auto sm:flex-row">
                <Button asChild variant="outline" className="w-full sm:w-auto">
                  <Link href="/projects">
                    <FolderOpen className="size-4" />
                    Open projects
                  </Link>
                </Button>
                <Button asChild className="w-full sm:w-auto">
                  <Link href="/dashboard">
                    <LayoutDashboard className="size-4" />
                    Dashboard
                  </Link>
                </Button>
              </div>
            }
          />
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {items.map(({ report, project }) => (
              <Link
                key={report.id}
                href={`/projects/${project.id}/reports/${report.id}`}
                className="block rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <Card className="h-full transition-colors hover:border-primary/40 hover:bg-muted/30">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <CardTitle className="truncate text-base leading-6">{report.title}</CardTitle>
                        <CardDescription className="mt-1 truncate">{project.title}</CardDescription>
                      </div>
                      <Badge variant={report.status === "completed" ? "success" : "secondary"}>{formatLabel(report.status)}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="grid gap-4 text-sm">
                    <div className="grid gap-3 sm:grid-cols-3">
                      <ReportMetric label="Score" value={report.overall_score === null ? "Unscored" : `${Math.round(report.overall_score)}%`} />
                      <ReportMetric label="Created" value={formatDate(report.created_at)} />
                      <ReportMetric label="Updated" value={formatDate(report.updated_at)} />
                    </div>
                    <p className="line-clamp-2 text-muted-foreground">
                      {report.executive_summary || "Open this report to review scores, fixes, questions, and markdown output."}
                    </p>
                    <div className="flex items-center gap-2 text-sm font-medium text-primary">
                      <ScrollText className="size-4" />
                      Open report
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}

function ReportsSkeleton() {
  return (
    <div className="grid gap-4 lg:grid-cols-2" aria-label="Loading reports">
      {Array.from({ length: 4 }).map((_, index) => (
        <Card key={index}>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <Skeleton className="h-5 w-2/3" />
                <Skeleton className="mt-3 h-4 w-1/2" />
              </div>
              <Skeleton className="h-6 w-20" />
            </div>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </div>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function SummaryCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{detail}</p>
      </CardContent>
    </Card>
  );
}

function ReportsState({
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

function ReportMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-border bg-background px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 truncate text-sm font-medium text-foreground">{value}</p>
    </div>
  );
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(value));
}

function formatLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
