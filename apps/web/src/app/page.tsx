import Link from "next/link";
import { ArrowRight, BrainCircuit, FileCheck2, MessagesSquare } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    title: "Research gap review",
    description: "Surface broad, unsupported, or outdated gap statements before supervisor review.",
    icon: BrainCircuit
  },
  {
    title: "Citation alignment",
    description: "Connect claims to references and identify weak support.",
    icon: FileCheck2
  },
  {
    title: "Visible agent log",
    description: "Show the handoffs and messages behind the final thesis health report.",
    icon: MessagesSquare
  }
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <section className="mx-auto flex min-h-[92vh] w-full max-w-7xl flex-col justify-center gap-10 px-4 py-10 sm:px-6 lg:px-8">
        <div className="max-w-3xl">
          <Badge variant="secondary">Powered by multi-agent review workflows</Badge>
          <h1 className="mt-5 text-4xl font-semibold tracking-normal text-primary-navy sm:text-5xl">
            ThesisForge
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-muted-foreground">
            A research quality-control workspace for reviewing thesis gaps, citations, methodology, results, and defense readiness.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/dashboard">
                Open dashboard
                <ArrowRight data-icon="inline-end" aria-hidden="true" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/projects">View projects</Link>
            </Button>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title}>
                <CardHeader>
                  <Icon aria-hidden="true" />
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-1 rounded-full bg-primary-soft" />
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>
    </main>
  );
}
