import { AppShell } from "@/components/layout/app-shell";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ReportsPage() {
  return (
    <AppShell>
      <Card>
        <CardHeader>
          <CardTitle>Reports</CardTitle>
          <CardDescription>Generated thesis health reports will be listed here.</CardDescription>
        </CardHeader>
      </Card>
    </AppShell>
  );
}
