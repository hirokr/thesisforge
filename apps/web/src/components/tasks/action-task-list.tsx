"use client";

import { CheckCircle2, CircleDashed, RefreshCw, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ActionTask, ActionTaskStatus } from "@/lib/api";
import { cn } from "@/lib/utils";

type ActionTaskListProps = {
  tasks: ActionTask[];
  isUpdating: boolean;
  updatingTaskId: string | null;
  error: string | null;
  onStatusChange: (taskId: string, status: ActionTaskStatus) => void;
};

export function ActionTaskList({ tasks, isUpdating, updatingTaskId, error, onStatusChange }: ActionTaskListProps) {
  const groups = groupTasks(tasks);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Action tasks</CardTitle>
        <CardDescription>Generated report fixes grouped by thesis area and sorted by priority.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {error ? <p className="rounded-md border border-danger/30 bg-danger/5 p-3 text-sm text-danger">{error}</p> : null}
        {tasks.length === 0 ? (
          <div className="rounded-md border border-border bg-background p-6 text-center">
            <CircleDashed className="mx-auto size-8 text-muted-foreground" />
            <h3 className="mt-3 text-sm font-semibold text-foreground">No action tasks yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">Run a review and open the final report to generate prioritized thesis fixes.</p>
          </div>
        ) : (
          groups.map((group) => (
            <section key={group.category} className="flex flex-col gap-3">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-sm font-semibold text-foreground">{formatLabel(group.category)}</h3>
                <Badge variant="secondary">{group.tasks.length}</Badge>
              </div>
              <div className="flex flex-col gap-3">
                {group.tasks.map((task) => {
                  const isTerminal = task.status === "completed" || task.status === "dismissed";
                  const isTaskUpdating = isUpdating && updatingTaskId === task.id;

                  return (
                    <article key={task.id} className={cn("rounded-md border border-border bg-background p-4", task.status === "dismissed" && "opacity-70")}>
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <h4 className="text-sm font-semibold text-foreground">{task.title}</h4>
                            <Badge variant={priorityVariant(task.priority)}>{formatLabel(task.priority)}</Badge>
                            <Badge variant={statusVariant(task.status)}>{formatLabel(task.status)}</Badge>
                          </div>
                          {task.description ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{task.description}</p> : null}
                        </div>
                        <div className="flex shrink-0 flex-wrap gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onStatusChange(task.id, "completed")}
                            disabled={isTerminal || isTaskUpdating}
                          >
                            {isTaskUpdating ? <RefreshCw className="size-4 animate-spin" /> : <CheckCircle2 className="size-4" />}
                            Complete
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onStatusChange(task.id, "dismissed")}
                            disabled={isTerminal || isTaskUpdating}
                          >
                            {isTaskUpdating ? <RefreshCw className="size-4 animate-spin" /> : <XCircle className="size-4" />}
                            Dismiss
                          </Button>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          ))
        )}
      </CardContent>
    </Card>
  );
}

function groupTasks(tasks: ActionTask[]): Array<{ category: string; tasks: ActionTask[] }> {
  const sortedTasks = [...tasks].sort((a, b) => priorityWeight(b.priority) - priorityWeight(a.priority) || a.title.localeCompare(b.title));
  const groups = new Map<string, ActionTask[]>();

  for (const task of sortedTasks) {
    const category = task.category || "uncategorized";
    groups.set(category, [...(groups.get(category) ?? []), task]);
  }

  return Array.from(groups.entries()).map(([category, groupedTasks]) => ({
    category,
    tasks: groupedTasks
  }));
}

function priorityWeight(value: string): number {
  switch (value.toLowerCase()) {
    case "critical":
    case "urgent":
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
  if (normalized === "critical" || normalized === "urgent" || normalized === "high") {
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

function statusVariant(status: ActionTaskStatus): "default" | "secondary" | "success" | "warning" | "danger" | "outline" {
  switch (status) {
    case "completed":
      return "success";
    case "dismissed":
      return "secondary";
    case "in_progress":
      return "warning";
    default:
      return "outline";
  }
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
