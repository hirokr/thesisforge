"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AuthPageGuard } from "@/components/auth/auth-page-guard";
import { GoogleOAuthButton } from "@/components/auth/google-oauth-button";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { friendlyErrorMessage } from "@/lib/errors";
import { getSupabaseClient } from "@/lib/supabase-client";

const registerSchema = z
  .object({
    fullName: z.string().min(2, "Enter your full name."),
    email: z.string().email("Enter a valid email address."),
    password: z.string().min(8, "Password must be at least 8 characters."),
    confirmPassword: z.string().min(8, "Confirm your password.")
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords must match."
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [formMessage, setFormMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      confirmPassword: ""
    }
  });

  async function onSubmit(values: RegisterFormValues) {
    setIsSubmitting(true);
    setFormError(null);
    setFormMessage(null);

    try {
      const supabase = getSupabaseClient();
      const { data, error } = await supabase.auth.signUp({
        email: values.email,
        password: values.password,
        options: {
          data: {
            full_name: values.fullName
          }
        }
      });

      if (error) {
        const message = error.message || "Could not create your account.";
        setFormError(message);
        toast({ title: "Signup failed", description: message, variant: "error" });
        return;
      }

      if (data.session) {
        router.push("/dashboard");
        return;
      }

      const message = "Check your email to verify your account before logging in.";
      setFormMessage(message);
      toast({ title: "Account created", description: message, variant: "success" });
    } catch (error) {
      const message = friendlyErrorMessage(error, "auth");
      setFormError(message);
      toast({ title: "Signup failed", description: message, variant: "error" });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthPageGuard>
      <main className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Create your account</CardTitle>
            <CardDescription>Start a thesis review workspace with email and password.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-5">
              <GoogleOAuthButton />
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <div className="h-px flex-1 bg-border" />
                <span>Email signup</span>
                <div className="h-px flex-1 bg-border" />
              </div>
              <form className="flex flex-col gap-5" onSubmit={form.handleSubmit(onSubmit)}>
                <FieldGroup>
                  <Field data-invalid={Boolean(form.formState.errors.fullName)}>
                    <FieldLabel htmlFor="fullName">Full name</FieldLabel>
                    <Input id="fullName" autoComplete="name" aria-invalid={Boolean(form.formState.errors.fullName)} {...form.register("fullName")} />
                    {form.formState.errors.fullName ? <FieldError>{form.formState.errors.fullName.message}</FieldError> : null}
                  </Field>
                  <Field data-invalid={Boolean(form.formState.errors.email)}>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} {...form.register("email")} />
                    {form.formState.errors.email ? <FieldError>{form.formState.errors.email.message}</FieldError> : null}
                  </Field>
                  <Field data-invalid={Boolean(form.formState.errors.password)}>
                    <FieldLabel htmlFor="password">Password</FieldLabel>
                    <Input id="password" type="password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} />
                    {form.formState.errors.password ? (
                      <FieldError>{form.formState.errors.password.message}</FieldError>
                    ) : (
                      <FieldDescription>Use at least 8 characters.</FieldDescription>
                    )}
                  </Field>
                  <Field data-invalid={Boolean(form.formState.errors.confirmPassword)}>
                    <FieldLabel htmlFor="confirmPassword">Confirm password</FieldLabel>
                    <Input
                      id="confirmPassword"
                      type="password"
                      autoComplete="new-password"
                      aria-invalid={Boolean(form.formState.errors.confirmPassword)}
                      {...form.register("confirmPassword")}
                    />
                    {form.formState.errors.confirmPassword ? <FieldError>{form.formState.errors.confirmPassword.message}</FieldError> : null}
                  </Field>
                </FieldGroup>
                {formError ? <FieldError>{formError}</FieldError> : null}
                {formMessage ? <FieldDescription>{formMessage}</FieldDescription> : null}
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Creating account" : "Create account"}
                  <ArrowRight data-icon="inline-end" aria-hidden="true" />
                </Button>
              </form>
            </div>
            <p className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link className="font-medium text-primary hover:text-primary-hover" href="/login">
                Log in
              </Link>
            </p>
          </CardContent>
        </Card>
      </main>
    </AuthPageGuard>
  );
}
