"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle2, FileText, Play, RefreshCw, ShieldQuestion } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/components/ui/field";
import { useToast } from "@/components/ui/toast";
import {
  getProject,
  listProjectDocuments,
  startAnalysisRun,
  type Document,
  type Project
} from "@/lib/api";
import { friendlyErrorMessage } from "@/lib/errors";
import { cn } from "@/lib/utils";

type ReviewType = "full_review" | "research_gap_review" | "defense_preparation";

const reviewTypes: Array<{
  value: ReviewType;
  label: string;
  description: string;
  includeResultsAgent: boolean;
}> = [
  {
    value: "full_review",
    label: "Full review",
    description: "Run the complete agent workflow with literature, citation, methodology, results, defense, and report checks.",
    includeResultsAgent: true
  },
  {
    value: "research_gap_review",
    label: "Research gap review",
    description: "Prioritize problem, gap, objective, and methodology alignment. The MVP worker still produces a full report.",
    includeResultsAgent: false
  },
  {
    value: "defense_preparation",
    label: "Defense preparation",
    description: "Focus the run on likely panel risks and defense questions. The MVP worker still produces a full report.",
    includeResultsAgent: false
  }
];

export default function RunReviewPage() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();
  const projectId = params.projectId;
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [reviewType, setReviewType] = useState<ReviewType>("full_review");
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startError, setStartError] = useState<string | null>(null);
  const { toast } = useToast();

  async function loadReviewWorkspace() {
    setIsLoading(true);
    setError(null);
    setStartError(null);

    try {
      const [projectResponse, documentsResponse] = await Promise.all([
        getProject(projectId),
        listProjectDocuments(projectId)
      ]);
      setProject(projectResponse);
      setDocuments(documentsResponse);
    } catch (err) {
      setError(friendlyErrorMessage(err, "permission"));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReviewWorkspace();
  }, [projectId]);

  const readiness = useMemo(() => buildReadiness(project, documents), [project, documents]);
  const hasBlockingWarnings = readiness.some((item) => item.required && !item.ready);
  const selectedReviewType = reviewTypes.find((type) => type.value === reviewType) ?? reviewTypes[0];

  async function startReview() {
    setIsStarting(true);
    setStartError(null);

    try {
      const run = await startAnalysisRun(projectId, {
        include_results_agent: selectedReviewType.includeResultsAgent
      });
      toast({ title: "Analysis started", description: "The thesis review is now queued.", variant: "success" });
      router.push(`/projects/${projectId}/runs/${run.id}`);
    } catch (err) {
      const message = friendlyErrorMessage(err, "analysis");
      setStartError(message);
      toast({ title: "Could not start analysis", description: message, variant: "error" });
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Button asChild variant="ghost" className="-ml-3 mb-2">
              <Link href={project ? `/projects/${project.id}` : "/dashboard"}>
                <ArrowLeft className="size-4" />
                Project overview
              </Link>
            </Button>
            <h1 className="text-2xl font-semibold text-foreground">Run thesis review</h1>
            <p className="mt-2 text-sm text-muted-foreground">{project?.title ?? "Prepare the agent workflow."}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant={hasBlockingWarnings ? "warning" : "success"}>
              {hasBlockingWarnings ? "Needs attention" : "Ready"}
            </Badge>
            <Badge variant="outline">{documents.length} documents</Badge>
          </div>
        </div>

        {isLoading ? (
          <ReviewState icon={<RefreshCw className="size-5 animate-spin" />} title="Loading review workspace" description="Checking project details and uploaded thesis materials." />
        ) : error ? (
          <ReviewState
            icon={<AlertCircle className="size-5" />}
            title="Review workspace unavailable"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadReviewWorkspace()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : (
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
            <Card>
              <CardHeader>
                <CardTitle>Readiness checklist</CardTitle>
                <CardDescription>Review agents work best with thesis context and at least one parsed draft.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3">
                {readiness.map((item) => (
                  <ChecklistItem key={item.label} item={item} />
                ))}
                {hasBlockingWarnings ? (
                  <div className="rounded-md border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-foreground">
                    Missing required inputs can make the review shallow. You can still start a run after adding the missing material.
                  </div>
                ) : null}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Review settings</CardTitle>
                <CardDescription>Select the workflow emphasis and start a background analysis run.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-5">
                <Field>
                  <FieldLabel htmlFor="reviewType">Review type</FieldLabel>
                  <select
                    id="reviewType"
                    value={reviewType}
                    onChange={(event) => setReviewType(event.target.value as ReviewType)}
                    className={cn(
                      "h-10 rounded-md border border-input bg-card px-3 text-sm shadow-sm",
                      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    )}
                  >
                    {reviewTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <FieldDescription>{selectedReviewType.description}</FieldDescription>
                </Field>

                <div className="rounded-md border border-border bg-background p-4">
                  <div className="flex items-start gap-3">
                    <ShieldQuestion className="mt-0.5 size-5 text-primary" />
                    <div>
                      <h2 className="text-sm font-medium text-foreground">Background run</h2>
                      <p className="mt-1 text-sm text-muted-foreground">
                        The API queues the analysis and the next page tracks status, current agent, and progress.
                      </p>
                    </div>
                  </div>
                </div>

                {startError ? <FieldError>{startError}</FieldError> : null}

                <Button className="w-full" onClick={() => void startReview()} disabled={isStarting || hasBlockingWarnings}>
                  {isStarting ? <RefreshCw className="size-4 animate-spin" /> : <Play className="size-4" />}
                  {isStarting ? "Starting review" : "Start analysis run"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}

type ChecklistEntry = {
  label: string;
  detail: string;
  ready: boolean;
  required: boolean;
};

function buildReadiness(project: Project | null, documents: Document[]): ChecklistEntry[] {
  const projectDetailsPresent = Boolean(
    project?.title?.trim() &&
      project.problem_statement?.trim() &&
      project.research_gap?.trim() &&
      project.objectives?.trim() &&
      project.methodology_summary?.trim()
  );
  const thesisContentPresent = documents.some(
    (document) =>
      document.document_type === "thesis_draft" &&
      (document.parse_status === "parsed" || Boolean(document.raw_text?.trim()))
  );
  const referencesPresent = documents.some((document) => document.document_type === "reference_file");

  return [
    {
      label: "Project details present",
      detail: projectDetailsPresent
        ? "Problem, gap, objectives, and methodology are available."
        : "Add problem, gap, objectives, and methodology before running a useful review.",
      ready: projectDetailsPresent,
      required: true
    },
    {
      label: "Thesis content present",
      detail: thesisContentPresent
        ? "At least one parsed thesis draft is available."
        : "Upload or paste a thesis draft so the agents can inspect actual content.",
      ready: thesisContentPresent,
      required: true
    },
    {
      label: "References present",
      detail: referencesPresent
        ? "Reference material is available for citation checks."
        : "References are optional, but citation findings will be limited without them.",
      ready: referencesPresent,
      required: false
    }
  ];
}

function ChecklistItem({ item }: { item: ChecklistEntry }) {
  const icon = item.ready ? (
    <CheckCircle2 className="size-5 text-success" />
  ) : item.required ? (
    <AlertCircle className="size-5 text-warning" />
  ) : (
    <FileText className="size-5 text-muted-foreground" />
  );

  return (
    <div className="flex gap-3 rounded-md border border-border bg-card p-4">
      <div className="mt-0.5">{icon}</div>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-medium text-foreground">{item.label}</h2>
          <Badge variant={item.ready ? "success" : item.required ? "warning" : "outline"}>
            {item.ready ? "Ready" : item.required ? "Missing" : "Optional"}
          </Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{item.detail}</p>
      </div>
    </div>
  );
}

function ReviewState({
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
