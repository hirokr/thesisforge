"use client";

import Link from "next/link";
import { AlertCircle, FileText, FolderPlus, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { listProjects, type Project } from "@/lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    setIsLoading(true);
    setError(null);

    try {
      setProjects(await listProjects());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load projects.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  const stats = useMemo(
    () => [
      { label: "Active projects", value: String(projects.length), badge: projects.length > 0 ? "In progress" : "Ready" },
      {
        label: "Average score",
        value: formatAverageScore(projects),
        badge: "Latest reports"
      },
      {
        label: "Updated recently",
        value: String(countRecentlyUpdated(projects)),
        badge: "Last 7 days"
      }
    ],
    [projects]
  );

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
            <p className="mt-2 text-sm text-muted-foreground">Track thesis projects, recent progress, and report readiness.</p>
          </div>
          <Button asChild>
            <Link href="/projects/new">
              <FolderPlus className="size-4" />
              Create project
            </Link>
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {stats.map((stat) => (
            <Card key={stat.label}>
              <CardHeader>
                <CardDescription>{stat.label}</CardDescription>
                <CardTitle className="text-3xl">{stat.value}</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge variant="secondary">{stat.badge}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>

        {isLoading ? (
          <DashboardState icon={<RefreshCw className="size-5 animate-spin" />} title="Loading projects" description="Fetching your thesis workspace." />
        ) : error ? (
          <DashboardState
            icon={<AlertCircle className="size-5" />}
            title="Could not load projects"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadProjects()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : projects.length === 0 ? (
          <DashboardState
            icon={<FileText className="size-5" />}
            title="No projects yet"
            description="Create your first thesis project to start reviewing drafts and research materials."
            action={
              <Button asChild>
                <Link href="/projects/new">
                  <FolderPlus className="size-4" />
                  Create project
                </Link>
              </Button>
            }
          />
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {projects.map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`} className="block rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                <Card className="h-full transition-colors hover:border-primary/40 hover:bg-muted/30">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <CardTitle className="truncate text-base leading-6">{project.title}</CardTitle>
                        <CardDescription className="mt-1">{project.research_area || "Research area not set"}</CardDescription>
                      </div>
                      <Badge variant="secondary">{project.status}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="grid gap-4 text-sm">
                    <div className="grid gap-3 sm:grid-cols-3">
                      <ProjectMetric label="Stage" value={project.thesis_stage || "Not set"} />
                      <ProjectMetric label="Score" value={project.latest_score === null ? "No report" : `${Math.round(project.latest_score)}%`} />
                      <ProjectMetric label="Updated" value={formatDate(project.updated_at)} />
                    </div>
                    {project.problem_statement ? (
                      <p className="line-clamp-2 text-muted-foreground">{project.problem_statement}</p>
                    ) : null}
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

function DashboardState({
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

function ProjectMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-border bg-background px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 truncate text-sm font-medium text-foreground">{value}</p>
    </div>
  );
}

function formatAverageScore(projects: Project[]): string {
  const scores = projects.flatMap((project) => (project.latest_score === null ? [] : [project.latest_score]));
  if (scores.length === 0) {
    return "-";
  }

  const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
  return `${Math.round(average)}%`;
}

function countRecentlyUpdated(projects: Project[]): number {
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  return projects.filter((project) => new Date(project.updated_at).getTime() >= sevenDaysAgo).length;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(value));
}
