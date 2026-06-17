"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { getSupabaseClient } from "@/lib/supabase-client";

function getOAuthError() {
  const queryParams = new URLSearchParams(window.location.search);
  const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));

  return queryParams.get("error_description") || queryParams.get("error") || hashParams.get("error_description") || hashParams.get("error");
}

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const supabase = getSupabaseClient();

    async function finishSignIn() {
      const oauthError = getOAuthError();
      const code = new URLSearchParams(window.location.search).get("code");

      if (oauthError) {
        router.replace(`/login?error=${encodeURIComponent("Google login failed. Please try again.")}`);
        return;
      }

      if (code) {
        const { error } = await supabase.auth.exchangeCodeForSession(code);

        if (error) {
          router.replace(`/login?error=${encodeURIComponent("Google login could not be completed.")}`);
          return;
        }
      }

      const { data } = await supabase.auth.getSession();

      if (data.session) {
        router.replace("/dashboard");
        return;
      }

      router.replace(`/login?error=${encodeURIComponent("Google login could not be completed.")}`);
    }

    void finishSignIn();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="rounded-md border border-border bg-card px-5 py-4 text-sm text-muted-foreground shadow-sm">
        Completing Google login
      </div>
    </main>
  );
}
