"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, FileUp, Play, RefreshCw, ScrollText } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getProject, listProjectDocuments, type Document, type Project } from "@/lib/api";

export default function ProjectOverviewPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params.projectId;
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadProject() {
    setIsLoading(true);
    setError(null);

    try {
      const [projectResponse, documentsResponse] = await Promise.all([
        getProject(projectId),
        listProjectDocuments(projectId)
      ]);
      setProject(projectResponse);
      setDocuments(documentsResponse);
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

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
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
                <Button>
                  <Play className="size-4" />
                  Run thesis review
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
                <CardHeader>
                  <CardTitle>Thesis metadata</CardTitle>
                  <CardDescription>Core context for the review agents.</CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <MetadataBlock label="Problem statement" value={project.problem_statement} />
                  <MetadataBlock label="Research gap" value={project.research_gap} />
                  <MetadataBlock label="Objectives" value={project.objectives} />
                  <MetadataBlock label="Methodology" value={project.methodology_summary} />
                  <MetadataBlock label="Dataset" value={project.dataset_summary} />
                  <MetadataBlock label="Results" value={project.results_summary} />
                </CardContent>
              </Card>

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
                  <Button variant="outline" className="justify-start">
                    <Play className="size-4" />
                    Run review
                  </Button>
                  <Button asChild variant="outline" className="justify-start" aria-disabled={project.latest_score === null}>
                    <Link href="/reports">
                      <ScrollText className="size-4" />
                      View latest report
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
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
