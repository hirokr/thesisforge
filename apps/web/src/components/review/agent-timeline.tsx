"use client";

import { AlertTriangle, CheckCircle2, Circle, Clock3, Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type RunStatus = "queued" | "running" | "completed" | "failed" | "partial" | string;
type AgentStatus = "waiting" | "running" | "completed" | "failed" | "partial";

type AgentTimelineProps = {
  runStatus: RunStatus;
  currentAgent: string | null;
  progressPercentage: number;
};

const workflowAgents = [
  {
    slug: "literature-review",
    name: "Literature Review",
    description: "Themes, citation support, and literature gaps"
  },
  {
    slug: "research-gap",
    name: "Research Gap",
    description: "Problem, gap, objectives, and evidence alignment"
  },
  {
    slug: "citation",
    name: "Citation",
    description: "Claim support and weak citation checks"
  },
  {
    slug: "methodology-consistency",
    name: "Methodology",
    description: "Method, dataset, baseline, and objective consistency"
  },
  {
    slug: "results-interpretation",
    name: "Results",
    description: "Overclaiming, comparisons, and discussion points"
  },
  {
    slug: "defense-preparation",
    name: "Defense",
    description: "Panel risks and likely thesis defense questions"
  },
  {
    slug: "report-generator",
    name: "Report",
    description: "Final score, risks, priorities, and action tasks"
  }
] as const;

export function AgentTimeline({ runStatus, currentAgent, progressPercentage }: AgentTimelineProps) {
  const statuses = getAgentStatuses(runStatus, currentAgent, progressPercentage);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent timeline</CardTitle>
        <CardDescription>Workflow order for this thesis review run.</CardDescription>
      </CardHeader>
      <CardContent>
        <ol className="grid gap-3 lg:grid-cols-7">
          {workflowAgents.map((agent, index) => {
            const status = statuses[agent.slug] ?? "waiting";
            const isLast = index === workflowAgents.length - 1;

            return (
              <li key={agent.slug} className="relative min-w-0">
                {!isLast ? (
                  <div
                    className={cn(
                      "absolute left-5 top-10 hidden h-px w-[calc(100%+0.75rem)] lg:block",
                      status === "completed" ? "bg-success" : "bg-border"
                    )}
                  />
                ) : null}
                <div className={cn("relative z-10 h-full rounded-md border bg-background p-3", getItemClass(status))}>
                  <div className="mb-3 flex items-start justify-between gap-2">
                    <div className={cn("flex size-9 shrink-0 items-center justify-center rounded-md", getIconClass(status))}>
                      <StatusIcon status={status} />
                    </div>
                    <Badge variant={getBadgeVariant(status)} className="capitalize">
                      {status}
                    </Badge>
                  </div>
                  <h3 className="break-words text-sm font-semibold leading-5 text-foreground">{agent.name}</h3>
                  <p className="mt-2 min-h-12 text-xs leading-5 text-muted-foreground">{agent.description}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}

function getAgentStatuses(runStatus: RunStatus, currentAgent: string | null, progressPercentage: number): Record<string, AgentStatus> {
  const statuses = Object.fromEntries(workflowAgents.map((agent) => [agent.slug, "waiting" as AgentStatus]));

  if (runStatus === "completed") {
    return Object.fromEntries(workflowAgents.map((agent) => [agent.slug, "completed" as AgentStatus]));
  }

  const currentIndex = currentAgent ? workflowAgents.findIndex((agent) => agent.slug === currentAgent) : -1;
  const inferredCompletedCount = Math.max(0, Math.min(workflowAgents.length, Math.floor((progressPercentage / 100) * workflowAgents.length)));
  const activeIndex = currentIndex >= 0 ? currentIndex : Math.min(inferredCompletedCount, workflowAgents.length - 1);

  workflowAgents.forEach((agent, index) => {
    if (index < activeIndex) {
      statuses[agent.slug] = "completed";
    }
  });

  if (runStatus === "failed") {
    statuses[workflowAgents[activeIndex]?.slug ?? workflowAgents[0].slug] = "failed";
    return statuses;
  }

  if (runStatus === "partial") {
    statuses[workflowAgents[activeIndex]?.slug ?? workflowAgents[0].slug] = "partial";
    return statuses;
  }

  if (runStatus === "running") {
    statuses[workflowAgents[activeIndex]?.slug ?? workflowAgents[0].slug] = "running";
  }

  return statuses;
}

function StatusIcon({ status }: { status: AgentStatus }) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="size-5" />;
    case "running":
      return <Loader2 className="size-5 animate-spin" />;
    case "failed":
      return <AlertTriangle className="size-5" />;
    case "partial":
      return <Clock3 className="size-5" />;
    default:
      return <Circle className="size-5" />;
  }
}

function getBadgeVariant(status: AgentStatus): "default" | "secondary" | "success" | "warning" | "danger" | "outline" {
  switch (status) {
    case "completed":
      return "success";
    case "running":
      return "default";
    case "failed":
      return "danger";
    case "partial":
      return "warning";
    default:
      return "outline";
  }
}

function getItemClass(status: AgentStatus): string {
  switch (status) {
    case "completed":
      return "border-success/30";
    case "running":
      return "border-primary/40 ring-2 ring-primary/15";
    case "failed":
      return "border-danger/40 bg-danger/5";
    case "partial":
      return "border-warning/40 bg-warning/5";
    default:
      return "border-border";
  }
}

function getIconClass(status: AgentStatus): string {
  switch (status) {
    case "completed":
      return "bg-success/10 text-success";
    case "running":
      return "bg-primary-soft text-primary";
    case "failed":
      return "bg-danger/10 text-danger";
    case "partial":
      return "bg-warning/10 text-warning";
    default:
      return "bg-muted text-muted-foreground";
  }
}
