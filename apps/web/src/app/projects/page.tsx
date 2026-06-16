import { Plus } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ProjectsPage() {
  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Projects</h1>
            <p className="mt-2 text-sm text-muted-foreground">Create and review thesis projects.</p>
          </div>
          <Button>
            <Plus data-icon="inline-start" aria-hidden="true" />
            New Project
          </Button>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>No projects yet</CardTitle>
            <CardDescription>Project CRUD arrives in the next implementation phase.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-dashed border-border bg-muted p-8 text-sm text-muted-foreground">
              Once the API is connected, thesis projects will appear here.
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
