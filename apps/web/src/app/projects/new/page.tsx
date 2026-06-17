"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { createProject } from "@/lib/api";
import { cn } from "@/lib/utils";

const projectSchema = z.object({
  title: z.string().trim().min(1, "Enter a thesis title."),
  research_area: z.string().trim().optional(),
  thesis_stage: z.string().trim().optional(),
  problem_statement: z.string().trim().optional(),
  research_gap: z.string().trim().optional(),
  objectives: z.string().trim().optional(),
  methodology_summary: z.string().trim().optional(),
  dataset_summary: z.string().trim().optional(),
  results_summary: z.string().trim().optional()
});

type ProjectFormValues = z.infer<typeof projectSchema>;

const longFields: Array<{
  name: keyof Pick<
    ProjectFormValues,
    "problem_statement" | "research_gap" | "objectives" | "methodology_summary" | "dataset_summary" | "results_summary"
  >;
  label: string;
}> = [
  { name: "problem_statement", label: "Problem statement" },
  { name: "research_gap", label: "Research gap" },
  { name: "objectives", label: "Objectives" },
  { name: "methodology_summary", label: "Methodology summary" },
  { name: "dataset_summary", label: "Dataset summary" },
  { name: "results_summary", label: "Results summary" }
];

export default function CreateProjectPage() {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      research_area: "",
      thesis_stage: "",
      problem_statement: "",
      research_gap: "",
      objectives: "",
      methodology_summary: "",
      dataset_summary: "",
      results_summary: ""
    }
  });

  async function onSubmit(values: ProjectFormValues) {
    setSubmitError(null);

    try {
      const project = await createProject(normalizeProjectPayload(values));
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Could not create project.");
    }
  }

  return (
    <AppShell>
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Button asChild variant="ghost" className="-ml-3 mb-2">
              <Link href="/dashboard">
                <ArrowLeft className="size-4" />
                Dashboard
              </Link>
            </Button>
            <h1 className="text-2xl font-semibold text-foreground">Create project</h1>
            <p className="mt-2 text-sm text-muted-foreground">Capture the thesis context agents will use during review.</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Thesis details</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="grid gap-5" onSubmit={handleSubmit(onSubmit)}>
              <div className="grid gap-5 sm:grid-cols-2">
                <Field>
                  <FieldLabel htmlFor="title">Thesis title</FieldLabel>
                  <Input id="title" placeholder="e.g. Explainable fake news detection" {...register("title")} />
                  <FieldError>{errors.title?.message}</FieldError>
                </Field>
                <Field>
                  <FieldLabel htmlFor="research_area">Research area</FieldLabel>
                  <Input id="research_area" placeholder="e.g. Natural language processing" {...register("research_area")} />
                  <FieldError>{errors.research_area?.message}</FieldError>
                </Field>
                <Field>
                  <FieldLabel htmlFor="thesis_stage">Thesis stage</FieldLabel>
                  <Input id="thesis_stage" placeholder="Proposal, draft, final review" {...register("thesis_stage")} />
                  <FieldError>{errors.thesis_stage?.message}</FieldError>
                </Field>
              </div>

              <div className="grid gap-5">
                {longFields.map((field) => (
                  <Field key={field.name}>
                    <FieldLabel htmlFor={field.name}>{field.label}</FieldLabel>
                    <textarea
                      id={field.name}
                      className={cn(
                        "min-h-28 w-full rounded-md border border-input bg-card px-3 py-2 text-sm shadow-sm transition-colors",
                        "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      )}
                      {...register(field.name)}
                    />
                    <FieldError>{errors[field.name]?.message}</FieldError>
                  </Field>
                ))}
              </div>

              {submitError ? (
                <div className="rounded-md border border-danger/20 bg-danger/5 px-4 py-3 text-sm text-danger">{submitError}</div>
              ) : null}

              <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <Button asChild variant="outline">
                  <Link href="/dashboard">Cancel</Link>
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  <Save className="size-4" />
                  {isSubmitting ? "Creating" : "Create project"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function normalizeProjectPayload(values: ProjectFormValues) {
  return Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value || null])) as ProjectFormValues;
}
