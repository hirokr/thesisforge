"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type PriorityFix = {
  title: string;
  description: string | null;
  category: string | null;
  priority: string | null;
};

type PriorityFixListProps = {
  structuredReport: Record<string, unknown> | null | undefined;
};

export function PriorityFixList({ structuredReport }: PriorityFixListProps) {
  const priorityFixes = extractPriorityFixes(structuredReport);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Priority fixes</CardTitle>
        <CardDescription>Recommended thesis improvements sorted by urgency.</CardDescription>
      </CardHeader>
      <CardContent>
        {priorityFixes.length === 0 ? (
          <EmptyMessage text="No priority fixes were included in this report." />
        ) : (
          <div className="flex flex-col gap-3">
            {priorityFixes.map((fix, index) => (
              <div key={`${fix.title}-${index}`} className="rounded-md border border-border bg-background p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h2 className="text-sm font-semibold text-foreground">{fix.title}</h2>
                  {fix.priority ? <Badge variant={priorityVariant(fix.priority)}>{formatLabel(fix.priority)}</Badge> : null}
                </div>
                {fix.category ? <p className="mt-2 text-xs font-medium uppercase tracking-normal text-muted-foreground">{formatLabel(fix.category)}</p> : null}
                {fix.description ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{fix.description}</p> : null}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function extractPriorityFixes(structuredReport: Record<string, unknown> | null | undefined): PriorityFix[] {
  const rawItems = readArray(structuredReport, "priority_fixes");
  return rawItems
    .map((item) => {
      if (typeof item === "string") {
        return { title: item, description: null, category: null, priority: "medium" };
      }
      if (!isRecord(item)) {
        return null;
      }
      return {
        title: readString(item, "title") || readString(item, "task") || readString(item, "recommendation") || "Priority fix",
        description: readString(item, "description") || readString(item, "details"),
        category: readString(item, "category"),
        priority: readString(item, "priority") || readString(item, "severity")
      };
    })
    .filter((item): item is PriorityFix => item !== null)
    .sort((a, b) => priorityWeight(b.priority) - priorityWeight(a.priority));
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
