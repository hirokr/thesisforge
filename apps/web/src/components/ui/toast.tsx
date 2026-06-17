"use client";

import { AlertCircle, CheckCircle2, Info, TriangleAlert, X } from "lucide-react";
import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type ToastVariant = "success" | "warning" | "error" | "info";

type ToastInput = {
  title: string;
  description?: string;
  variant?: ToastVariant;
};

type Toast = ToastInput & {
  id: string;
  variant: ToastVariant;
};

type ToastContextValue = {
  toast: (input: ToastInput) => void;
  dismissToast: (id: string) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id));
  }, []);

  const toast = useCallback(
    (input: ToastInput) => {
      const id = crypto.randomUUID();
      const nextToast: Toast = {
        id,
        variant: input.variant ?? "info",
        title: input.title,
        description: input.description
      };

      setToasts((currentToasts) => [nextToast, ...currentToasts].slice(0, 4));
      window.setTimeout(() => dismissToast(id), input.variant === "error" ? 7000 : 4500);
    },
    [dismissToast]
  );

  const value = useMemo(() => ({ toast, dismissToast }), [toast, dismissToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3" aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={() => dismissToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used inside ToastProvider.");
  }

  return context;
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const Icon = iconForVariant(toast.variant);

  return (
    <div className={cn("flex gap-3 rounded-md border bg-card p-4 text-sm shadow-lg", toneForVariant(toast.variant))}>
      <Icon className="mt-0.5 size-5 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="font-medium text-foreground">{toast.title}</p>
        {toast.description ? <p className="mt-1 text-muted-foreground">{toast.description}</p> : null}
      </div>
      <Button type="button" variant="ghost" size="icon" className="-mr-2 -mt-2 size-8 shrink-0" onClick={onDismiss} aria-label="Dismiss message">
        <X className="size-4" />
      </Button>
    </div>
  );
}

function iconForVariant(variant: ToastVariant) {
  switch (variant) {
    case "success":
      return CheckCircle2;
    case "warning":
      return TriangleAlert;
    case "error":
      return AlertCircle;
    default:
      return Info;
  }
}

function toneForVariant(variant: ToastVariant): string {
  switch (variant) {
    case "success":
      return "border-success/30 [&>svg]:text-success";
    case "warning":
      return "border-warning/30 [&>svg]:text-warning";
    case "error":
      return "border-danger/30 [&>svg]:text-danger";
    default:
      return "border-primary/30 [&>svg]:text-primary";
  }
}
