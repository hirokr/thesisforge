"use client";

import { Activity, HelpCircle, ShieldQuestion } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type ScoreValue = number | null;

type ScoreCardProps = {
  label: string;
  score: ScoreValue;
  description?: string;
  prominent?: boolean;
};

type ScoreBreakdownCardsProps = {
  scoreBreakdown: Record<string, unknown> | null | undefined;
};

const scoreAreas = [
  { key: "gap", aliases: ["gap_score", "research_gap", "research_gap_score", "literature_gap"], label: "Gap score" },
  { key: "citation", aliases: ["citation_score", "citations", "citation_support"], label: "Citation score" },
  {
    key: "methodology",
    aliases: ["methodology_score", "methodology_consistency", "methodology_objective_alignment", "baseline_models"],
    label: "Methodology score"
  },
  { key: "results", aliases: ["results_score", "results_interpretation"], label: "Results score" },
  { key: "defense", aliases: ["defense_score", "defense_preparation"], label: "Defense score" }
] as const;

export function OverallScoreCard({ score, createdAt }: { score: ScoreValue; createdAt: string }) {
  return (
    <ScoreCard
      label="Overall score"
      score={score}
      description={formatDateTime(createdAt)}
      prominent
    />
  );
}

export function ScoreBreakdownCards({ scoreBreakdown }: ScoreBreakdownCardsProps) {
  const entries = getScoreEntries(scoreBreakdown);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Score breakdown</CardTitle>
        <CardDescription>Agent-level score signals from the structured report.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {entries.map((entry) => (
            <ScoreCard key={entry.key} label={entry.label} score={entry.score} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ScoreCard({ label, score, description, prominent = false }: ScoreCardProps) {
  const status = getScoreStatus(score);
  const Icon = score === null ? HelpCircle : prominent ? ShieldQuestion : Activity;

  return (
    <Card className={cn("overflow-hidden", getScoreCardClass(score))}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className={prominent ? "text-lg" : "text-sm"}>{label}</CardTitle>
            {description ? <CardDescription>{description}</CardDescription> : null}
          </div>
          <div className={cn("flex size-9 shrink-0 items-center justify-center rounded-md", getIconClass(score))}>
            <Icon className="size-5" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className={cn("flex min-h-28 flex-col justify-end rounded-md border bg-background/70 p-4", prominent && "min-h-44 items-center justify-center text-center")}>
          <p className={cn("font-semibold leading-none", prominent ? "text-5xl" : "text-3xl")}>{formatScore(score)}</p>
          <p className="mt-2 text-sm text-muted-foreground">{score === null ? "Score unavailable" : "out of 100"}</p>
          <p className={cn("mt-3 text-xs font-medium uppercase tracking-normal", getStatusTextClass(score))}>{status}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function getScoreEntries(scoreBreakdown: Record<string, unknown> | null | undefined) {
  return scoreAreas.map((area) => ({
    key: area.key,
    label: area.label,
    score: readScore(scoreBreakdown, area.key, area.aliases)
  }));
}

function readScore(scoreBreakdown: Record<string, unknown> | null | undefined, key: string, aliases: readonly string[]): ScoreValue {
  if (!scoreBreakdown) {
    return null;
  }

  const value = [key, ...aliases].map((candidate) => scoreBreakdown[candidate]).find((candidate) => candidate !== undefined);
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function getScoreCardClass(score: ScoreValue): string {
  if (score === null) {
    return "border-border";
  }
  if (score >= 80) {
    return "border-success/30";
  }
  if (score >= 60) {
    return "border-warning/30";
  }
  return "border-danger/30";
}

function getIconClass(score: ScoreValue): string {
  if (score === null) {
    return "bg-muted text-muted-foreground";
  }
  if (score >= 80) {
    return "bg-success/10 text-success";
  }
  if (score >= 60) {
    return "bg-warning/10 text-warning";
  }
  return "bg-danger/10 text-danger";
}

function getStatusTextClass(score: ScoreValue): string {
  if (score === null) {
    return "text-muted-foreground";
  }
  if (score >= 80) {
    return "text-success";
  }
  if (score >= 60) {
    return "text-warning";
  }
  return "text-danger";
}

function getScoreStatus(score: ScoreValue): string {
  if (score === null) {
    return "Missing";
  }
  if (score >= 80) {
    return "Strong";
  }
  if (score >= 60) {
    return "Needs attention";
  }
  return "High risk";
}

function formatScore(score: ScoreValue): string {
  return score === null ? "N/A" : String(Math.round(score));
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
