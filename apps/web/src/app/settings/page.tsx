import { AppShell } from "@/components/layout/app-shell";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <AppShell>
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Account and workspace settings will be available after authentication is implemented.</CardDescription>
        </CardHeader>
      </Card>
    </AppShell>
  );
}
