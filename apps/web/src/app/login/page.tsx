"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AuthPageGuard } from "@/components/auth/auth-page-guard";
import { GoogleOAuthButton } from "@/components/auth/google-oauth-button";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { friendlyErrorMessage } from "@/lib/errors";
import { getSafeRedirectPath } from "@/lib/routes";
import { getSupabaseClient } from "@/lib/supabase-client";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password.")
});

type LoginFormValues = z.infer<typeof loginSchema>;

function getNextPath() {
  if (typeof window === "undefined") {
    return "/dashboard";
  }

  return getSafeRedirectPath(new URLSearchParams(window.location.search).get("next"));
}

export default function LoginPage() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  });

  useEffect(() => {
    const error = new URLSearchParams(window.location.search).get("error");

    if (error) {
      setFormError(error);
      toast({ title: "Login failed", description: error, variant: "error" });
    }
  }, [toast]);

  async function onSubmit(values: LoginFormValues) {
    setIsSubmitting(true);
    setFormError(null);

    try {
      const supabase = getSupabaseClient();
      const { error } = await supabase.auth.signInWithPassword(values);

      if (error) {
        const message = "Invalid email or password.";
        setFormError(message);
        toast({ title: "Login failed", description: message, variant: "error" });
        return;
      }

      router.push(getNextPath());
    } catch (error) {
      const message = friendlyErrorMessage(error, "auth");
      setFormError(message);
      toast({ title: "Login failed", description: message, variant: "error" });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthPageGuard>
      <main className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Log in</CardTitle>
            <CardDescription>Continue to your thesis review dashboard.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-5">
              <GoogleOAuthButton />
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <div className="h-px flex-1 bg-border" />
                <span>Email login</span>
                <div className="h-px flex-1 bg-border" />
              </div>
              <form className="flex flex-col gap-5" onSubmit={form.handleSubmit(onSubmit)}>
                <FieldGroup>
                  <Field data-invalid={Boolean(form.formState.errors.email)}>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} {...form.register("email")} />
                    {form.formState.errors.email ? <FieldError>{form.formState.errors.email.message}</FieldError> : null}
                  </Field>
                  <Field data-invalid={Boolean(form.formState.errors.password)}>
                    <FieldLabel htmlFor="password">Password</FieldLabel>
                    <Input id="password" type="password" autoComplete="current-password" aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} />
                    {form.formState.errors.password ? <FieldError>{form.formState.errors.password.message}</FieldError> : null}
                  </Field>
                </FieldGroup>
                {formError ? <FieldError>{formError}</FieldError> : null}
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Logging in" : "Log in"}
                  <ArrowRight data-icon="inline-end" aria-hidden="true" />
                </Button>
              </form>
            </div>
            <div className="mt-6 flex flex-col gap-2 text-center text-sm text-muted-foreground">
              <Link className="font-medium text-primary hover:text-primary-hover" href="/forgot-password">
                Forgot password?
              </Link>
              <p>
                New to ThesisForge?{" "}
                <Link className="font-medium text-primary hover:text-primary-hover" href="/register">
                  Create an account
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </main>
    </AuthPageGuard>
  );
}
