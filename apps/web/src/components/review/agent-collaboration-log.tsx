"use client";

import { AlertCircle, ArrowRight, MessagesSquare, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { listAgentMessages, type AgentMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

const POLL_INTERVAL_MS = 4000;

type AgentCollaborationLogProps = {
  runId: string;
  isLive: boolean;
};

export function AgentCollaborationLog({ runId, isLive }: AgentCollaborationLogProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadMessages({ initial = false }: { initial?: boolean } = {}) {
    if (initial) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError(null);

    try {
      setMessages(await listAgentMessages(runId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load agent messages.");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    void loadMessages({ initial: true });
  }, [runId]);

  useEffect(() => {
    if (!isLive || error) {
      return;
    }

    const pollId = window.setInterval(() => {
      void loadMessages();
    }, POLL_INTERVAL_MS);

    return () => window.clearInterval(pollId);
  }, [runId, isLive, error]);

  return (
    <Card>
      <CardHeader className="gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <CardTitle>Agent collaboration log</CardTitle>
          <CardDescription>{isLive ? "Agent handoffs update while the review is active." : "Agent handoffs saved for this run."}</CardDescription>
        </div>
        <Button variant="outline" className="w-full sm:w-auto" onClick={() => void loadMessages()} disabled={isRefreshing}>
          <RefreshCw className={cn("size-4", isRefreshing && "animate-spin")} />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <LogState icon={<RefreshCw className="size-5 animate-spin" />} title="Loading messages" description="Fetching agent handoffs for this run." />
        ) : error ? (
          <LogState
            icon={<AlertCircle className="size-5" />}
            title="Messages unavailable"
            description={error}
          />
        ) : messages.length === 0 ? (
          <LogState
            icon={<MessagesSquare className="size-5" />}
            title="No messages yet"
            description="Agent handoffs will appear here after the workflow starts sending collaboration events."
          />
        ) : (
          <ol className="space-y-3">
            {messages.map((message) => {
              const isAgentFailure = message.message_type === "agent_failure";
              const isLocalFallback = message.message_type === "handoff" && (message.status === "failed" || message.status === "local");

              return (
              <li
                key={message.id}
                className={cn(
                  "rounded-md border border-border bg-background p-4",
                  isAgentFailure && "border-danger/40 bg-danger/5"
                )}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-foreground">
                      <span>{formatAgent(message.from_agent_name, message.from_agent_slug, "System")}</span>
                      <ArrowRight className="size-4 text-muted-foreground" />
                      <span>{formatAgent(message.to_agent_name, message.to_agent_slug, "Workflow")}</span>
                    </div>
                    <p className="mt-2 break-words text-sm leading-6 text-muted-foreground">{message.summary || message.content}</p>
                  </div>
                  <div className="flex shrink-0 flex-wrap gap-2">
                    <Badge variant="outline">{formatLabel(message.message_type)}</Badge>
                    <Badge variant={isAgentFailure ? "danger" : "secondary"}>
                      {isLocalFallback ? "Saved locally" : formatLabel(message.status)}
                    </Badge>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-muted-foreground">
                  <span>{formatDateTime(message.created_at)}</span>
                  {message.task ? <span>{formatLabel(message.task)}</span> : null}
                </div>
              </li>
              );
            })}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}

function LogState({
  icon,
  title,
  description
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center gap-4 py-10 text-center">
      <div className="flex size-10 items-center justify-center rounded-md bg-primary-soft text-primary">{icon}</div>
      <div>
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

function formatAgent(name: string | null, slug: string | null, fallback: string): string {
  return name || (slug ? formatLabel(slug) : fallback);
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

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
