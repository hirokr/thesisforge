"use client";

import { CheckCircle2, ShieldQuestion } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type DefenseQuestion = {
  question: string;
  category: string | null;
  riskLevel: string | null;
  answerPoints: string[];
};

type DefenseQuestionsListProps = {
  structuredReport: Record<string, unknown> | null | undefined;
};

export function DefenseQuestionsList({ structuredReport }: DefenseQuestionsListProps) {
  const defenseQuestions = extractDefenseQuestions(structuredReport);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Defense questions</CardTitle>
        <CardDescription>Likely panel questions and answer preparation notes.</CardDescription>
      </CardHeader>
      <CardContent>
        {defenseQuestions.length === 0 ? (
          <EmptyMessage text="No defense questions were included in this report." />
        ) : (
          <div className="flex flex-col gap-3">
            {defenseQuestions.map((item, index) => (
              <div key={`${item.question}-${index}`} className="rounded-md border border-border bg-background p-4">
                <div className="flex gap-3">
                  <ShieldQuestion className="mt-0.5 size-5 shrink-0 text-primary" />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <h2 className="text-sm font-semibold text-foreground">{item.question}</h2>
                      {item.riskLevel ? <Badge variant={priorityVariant(item.riskLevel)}>{formatLabel(item.riskLevel)}</Badge> : null}
                    </div>
                    {item.category ? <p className="mt-2 text-xs font-medium uppercase tracking-normal text-muted-foreground">{formatLabel(item.category)}</p> : null}
                    {item.answerPoints.length > 0 ? (
                      <ul className="mt-3 flex flex-col gap-2 text-sm leading-6 text-muted-foreground">
                        {item.answerPoints.map((point) => (
                          <li key={point} className="flex gap-2">
                            <CheckCircle2 className="mt-1 size-4 shrink-0 text-success" />
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function extractDefenseQuestions(structuredReport: Record<string, unknown> | null | undefined): DefenseQuestion[] {
  const rawItems = readArray(structuredReport, "defense_questions");
  return rawItems
    .map((item) => {
      if (typeof item === "string") {
        return { question: item, category: null, riskLevel: null, answerPoints: [] };
      }
      if (!isRecord(item)) {
        return null;
      }
      return {
        question: readString(item, "question") || "Defense question",
        category: readString(item, "category"),
        riskLevel: readString(item, "risk_level") || readString(item, "riskLevel"),
        answerPoints: readStringArray(item, "suggested_answer_points")
      };
    })
    .filter((item): item is DefenseQuestion => item !== null)
    .sort((a, b) => priorityWeight(b.riskLevel) - priorityWeight(a.riskLevel));
}

function EmptyMessage({ text }: { text: string }) {
  return <p className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">{text}</p>;
}

function readArray(record: Record<string, unknown> | null | undefined, key: string): unknown[] {
  const value = record?.[key];
  return Array.isArray(value) ? value : [];
}

function readString(record: Record<string, unknown>, key: string): string | null {
  const value = record[key];
  return typeof value === "string" && value.trim() ? value : null;
}

function readStringArray(record: Record<string, unknown>, key: string): string[] {
  const value = record[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string" && item.trim().length > 0) : [];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function priorityWeight(value: string | null): number {
  switch (value?.toLowerCase()) {
    case "critical":
      return 4;
    case "high":
      return 3;
    case "medium":
      return 2;
    case "low":
      return 1;
    default:
      return 0;
  }
}

function priorityVariant(priority: string): "default" | "secondary" | "success" | "warning" | "danger" | "outline" {
  const normalized = priority.toLowerCase();
  if (normalized === "critical" || normalized === "high") {
    return "danger";
  }
  if (normalized === "medium") {
    return "warning";
  }
  if (normalized === "low") {
    return "secondary";
  }
  return "outline";
}

function formatLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
