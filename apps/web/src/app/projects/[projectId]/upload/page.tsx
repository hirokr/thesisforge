"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, FileText, FileUp, RefreshCw, Send, Upload } from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import {
  createTextDocument,
  getProject,
  listProjectDocuments,
  uploadProjectDocument,
  type Document,
  type Project
} from "@/lib/api";
import { friendlyErrorMessage } from "@/lib/errors";
import { cn } from "@/lib/utils";

const documentTypes = [
  { value: "thesis_draft", label: "Thesis draft" },
  { value: "reference_file", label: "Reference file" },
  { value: "result_file", label: "Result file" },
  { value: "supervisor_feedback", label: "Supervisor feedback" },
  { value: "other", label: "Other" }
];

export default function ProjectUploadPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params.projectId;
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const [isSubmittingText, setIsSubmittingText] = useState(false);
  const [fileType, setFileType] = useState("thesis_draft");
  const [textType, setTextType] = useState("thesis_draft");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [textTitle, setTextTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [textError, setTextError] = useState<string | null>(null);
  const { toast } = useToast();

  async function loadPage() {
    setIsLoading(true);
    setError(null);

    try {
      const [projectResponse, documentResponse] = await Promise.all([
        getProject(projectId),
        listProjectDocuments(projectId)
      ]);
      setProject(projectResponse);
      setDocuments(documentResponse);
    } catch (err) {
      setError(friendlyErrorMessage(err, "permission"));
    } finally {
      setIsLoading(false);
    }
  }

  async function reloadDocuments() {
    const documentResponse = await listProjectDocuments(projectId);
    setDocuments(documentResponse);
  }

  useEffect(() => {
    void loadPage();
  }, [projectId]);

  const parsedCount = useMemo(
    () => documents.filter((document) => document.parse_status === "parsed").length,
    [documents]
  );

  async function submitFileUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFileError(null);

    if (!selectedFile) {
      const message = "Choose a file to upload.";
      setFileError(message);
      toast({ title: "No file selected", description: message, variant: "warning" });
      return;
    }

    setIsUploadingFile(true);
    try {
      await uploadProjectDocument(projectId, fileType, selectedFile);
      setSelectedFile(null);
      event.currentTarget.reset();
      await reloadDocuments();
      toast({ title: "File uploaded", description: "The document was added to this project.", variant: "success" });
    } catch (err) {
      const message = friendlyErrorMessage(err, "upload");
      setFileError(message);
      toast({ title: "Upload failed", description: message, variant: "error" });
    } finally {
      setIsUploadingFile(false);
    }
  }

  async function submitPastedText(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTextError(null);

    if (!textTitle.trim()) {
      const message = "Enter a document title.";
      setTextError(message);
      toast({ title: "Title required", description: message, variant: "warning" });
      return;
    }

    if (!rawText.trim()) {
      const message = "Paste document text before submitting.";
      setTextError(message);
      toast({ title: "Text required", description: message, variant: "warning" });
      return;
    }

    setIsSubmittingText(true);
    try {
      await createTextDocument(projectId, {
        document_type: textType,
        title: textTitle.trim(),
        raw_text: rawText
      });
      setTextTitle("");
      setRawText("");
      await reloadDocuments();
      toast({ title: "Text saved", description: "The pasted document was added and parsed.", variant: "success" });
    } catch (err) {
      const message = friendlyErrorMessage(err, "upload");
      setTextError(message);
      toast({ title: "Save failed", description: message, variant: "error" });
    } finally {
      setIsSubmittingText(false);
    }
  }

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Button asChild variant="ghost" className="-ml-3 mb-2">
              <Link href={project ? `/projects/${project.id}` : "/dashboard"}>
                <ArrowLeft className="size-4" />
                Project overview
              </Link>
            </Button>
            <h1 className="text-2xl font-semibold text-foreground">Upload documents</h1>
            <p className="mt-2 text-sm text-muted-foreground">{project?.title ?? "Project materials"}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:min-w-72">
            <Metric label="Documents" value={String(documents.length)} />
            <Metric label="Parsed" value={String(parsedCount)} />
          </div>
        </div>

        {isLoading ? (
          <UploadPageSkeleton />
        ) : error ? (
          <UploadState
            icon={<AlertCircle className="size-5" />}
            title="Upload workspace unavailable"
            description={error}
            action={
              <Button variant="outline" onClick={() => void loadPage()}>
                <RefreshCw className="size-4" />
                Retry
              </Button>
            }
          />
        ) : (
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
            <div className="grid gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>File upload</CardTitle>
                  <CardDescription>PDF, DOCX, TXT, BIB, and CSV files up to 25 MB.</CardDescription>
                </CardHeader>
                <CardContent>
                  <form className="grid gap-4" onSubmit={submitFileUpload}>
                    <DocumentTypeSelect id="fileType" value={fileType} onChange={setFileType} />
                    <Field>
                      <FieldLabel htmlFor="file">File</FieldLabel>
                      <Input
                        id="file"
                        type="file"
                        accept=".pdf,.docx,.txt,.bib,.csv"
                        onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                      />
                      <FieldError>{fileError}</FieldError>
                    </Field>
                    <div className="flex justify-end">
                      <Button type="submit" className="w-full sm:w-auto" disabled={isUploadingFile}>
                        {isUploadingFile ? <RefreshCw className="size-4 animate-spin" /> : <Upload className="size-4" />}
                        {isUploadingFile ? "Uploading" : "Upload file"}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Pasted text</CardTitle>
                  <CardDescription>Save thesis sections directly as parsed text.</CardDescription>
                </CardHeader>
                <CardContent>
                  <form className="grid gap-4" onSubmit={submitPastedText}>
                    <div className="grid gap-4 md:grid-cols-2">
                      <DocumentTypeSelect id="textType" value={textType} onChange={setTextType} />
                      <Field>
                        <FieldLabel htmlFor="textTitle">Title</FieldLabel>
                        <Input id="textTitle" value={textTitle} onChange={(event) => setTextTitle(event.target.value)} />
                      </Field>
                    </div>
                    <Field>
                      <FieldLabel htmlFor="rawText">Text</FieldLabel>
                      <textarea
                        id="rawText"
                        value={rawText}
                        onChange={(event) => setRawText(event.target.value)}
                        rows={12}
                        className={cn(
                          "w-full rounded-md border border-input bg-card px-3 py-2 text-sm shadow-sm transition-colors",
                          "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        )}
                      />
                      <FieldError>{textError}</FieldError>
                    </Field>
                    <div className="flex justify-end">
                      <Button type="submit" className="w-full sm:w-auto" disabled={isSubmittingText}>
                        {isSubmittingText ? <RefreshCw className="size-4 animate-spin" /> : <Send className="size-4" />}
                        {isSubmittingText ? "Saving" : "Save text"}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader className="gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <CardTitle>Uploaded documents</CardTitle>
                  <CardDescription>{documents.length === 0 ? "No documents added yet." : `${documents.length} project documents.`}</CardDescription>
                </div>
                <Button variant="outline" size="sm" className="w-full sm:w-auto" onClick={() => void reloadDocuments()}>
                  <RefreshCw className="size-4" />
                  Refresh
                </Button>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <div className="flex flex-col items-center gap-3 rounded-md border border-dashed border-border px-4 py-10 text-center">
                    <FileUp className="size-6 text-muted-foreground" />
                    <p className="text-sm font-medium text-foreground">No uploads yet</p>
                    <p className="max-w-sm text-sm text-muted-foreground">
                      Upload a file or paste thesis text here to give the review agents source material.
                    </p>
                  </div>
                ) : (
                  <div className="grid gap-3">
                    {documents.map((document) => (
                      <DocumentRow key={document.id} document={document} />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function UploadPageSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]" aria-label="Loading upload workspace">
      <div className="grid gap-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-28" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent className="grid gap-4">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
            <div className="flex justify-end">
              <Skeleton className="h-10 w-28" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-28" />
            <Skeleton className="h-4 w-56" />
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </div>
            <Skeleton className="h-48" />
            <div className="flex justify-end">
              <Skeleton className="h-10 w-24" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-3">
            <Skeleton className="h-6 w-44" />
            <Skeleton className="h-4 w-36" />
          </div>
          <Skeleton className="h-9 w-24" />
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="rounded-md border border-border bg-background p-3">
                <div className="flex items-start gap-3">
                  <Skeleton className="size-9 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <Skeleton className="h-4 w-3/4" />
                    <div className="mt-3 flex gap-2">
                      <Skeleton className="h-6 w-24" />
                      <Skeleton className="h-6 w-20" />
                    </div>
                    <Skeleton className="mt-3 h-3 w-1/2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DocumentTypeSelect({
  id,
  value,
  onChange
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <Field>
      <FieldLabel htmlFor={id}>Document type</FieldLabel>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-10 w-full rounded-md border border-input bg-card px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {documentTypes.map((type) => (
          <option key={type.value} value={type.value}>
            {type.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

function DocumentRow({ document }: { document: Document }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <div className="flex items-start gap-3">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary">
          <FileText className="size-4" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="break-words text-sm font-medium text-foreground">{document.filename}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge variant="outline">{formatDocumentType(document.document_type)}</Badge>
            <ParseStatusBadge status={document.parse_status} />
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {formatBytes(document.size_bytes)} · {new Date(document.created_at).toLocaleDateString()}
          </p>
          {document.parse_metadata ? <MetadataSummary metadata={document.parse_metadata} /> : null}
        </div>
      </div>
    </div>
  );
}

function ParseStatusBadge({ status }: { status: string }) {
  if (status === "parsed") {
    return <Badge className="bg-success text-white hover:bg-success">Parsed</Badge>;
  }

  if (status === "failed") {
    return <Badge variant="danger">Failed</Badge>;
  }

  return <Badge variant="secondary">{status}</Badge>;
}

function MetadataSummary({ metadata }: { metadata: Record<string, unknown> }) {
  const rowCount = metadata.row_count;
  const columnNames = metadata.column_names;

  if (typeof rowCount !== "number" || !Array.isArray(columnNames)) {
    return null;
  }

  return (
    <p className="mt-2 text-xs text-muted-foreground">
      {rowCount} rows · {columnNames.length} columns
    </p>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-card px-4 py-3">
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <p className="mt-1 text-xl font-semibold text-foreground">{value}</p>
    </div>
  );
}

function UploadState({
  icon,
  title,
  description,
  action
}: {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
        <div className="flex size-10 items-center justify-center rounded-md bg-primary-soft text-primary">{icon}</div>
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
        </div>
        {action}
      </CardContent>
    </Card>
  );
}

function formatDocumentType(type: string) {
  return documentTypes.find((documentType) => documentType.value === type)?.label ?? type.replaceAll("_", " ");
}

function formatBytes(value: number | null) {
  if (value === null) {
    return "Size unknown";
  }

  if (value < 1024) {
    return `${value} B`;
  }

  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }

  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}
