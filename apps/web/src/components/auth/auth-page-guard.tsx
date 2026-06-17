"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getSafeRedirectPath } from "@/lib/routes";
import { getSupabaseClient } from "@/lib/supabase-client";

export function AuthPageGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isCheckingSession, setIsCheckingSession] = useState(true);

  useEffect(() => {
    const supabase = getSupabaseClient();
    let isMounted = true;

    async function checkSession() {
      const { data } = await supabase.auth.getSession();

      if (!isMounted) {
        return;
      }

      if (data.session) {
        const params = new URLSearchParams(window.location.search);
        router.replace(getSafeRedirectPath(params.get("next")));
        return;
      }

      setIsCheckingSession(false);
    }

    void checkSession();

    return () => {
      isMounted = false;
    };
  }, [router]);

  if (isCheckingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="rounded-md border border-border bg-card px-5 py-4 text-sm text-muted-foreground shadow-sm">
          Checking your session
        </div>
      </main>
    );
  }

  return children;
}
