import Link from "next/link";
import { FileText, LayoutDashboard } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ReportsPage() {
  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Reports</h1>
          <p className="mt-2 text-sm text-muted-foreground">Review generated thesis health reports and follow-up actions.</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>No reports yet</CardTitle>
            <CardDescription>Run your first thesis review to generate a scored report, priority fixes, and defense questions.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center gap-4 rounded-md border border-dashed border-border bg-background px-4 py-10 text-center">
              <div className="flex size-10 items-center justify-center rounded-md bg-primary-soft text-primary">
                <FileText className="size-5" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Reports appear after an analysis run completes.</p>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Open a project from the dashboard, add thesis material if needed, then start a review.
                </p>
              </div>
              <Button asChild>
                <Link href="/dashboard">
                  <LayoutDashboard className="size-4" />
                  Go to dashboard
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
