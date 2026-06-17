"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";

import { getSupabaseClient } from "@/lib/supabase-client";

function AuthLoadingState() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="rounded-md border border-border bg-card px-5 py-4 text-sm text-muted-foreground shadow-sm">
        Checking your session
      </div>
    </main>
  );
}

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [isCheckingSession, setIsCheckingSession] = useState(true);

  useEffect(() => {
    const supabase = getSupabaseClient();
    let isMounted = true;

    async function checkSession() {
      const { data } = await supabase.auth.getSession();

      if (!isMounted) {
        return;
      }

      setSession(data.session);
      setIsCheckingSession(false);

      if (!data.session) {
        const next = encodeURIComponent(pathname);
        router.replace(`/login?next=${next}`);
      }
    }

    void checkSession();

    const {
      data: { subscription }
    } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      setSession(currentSession);

      if (!currentSession) {
        const next = encodeURIComponent(pathname);
        router.replace(`/login?next=${next}`);
      }
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, [pathname, router]);

  if (isCheckingSession || !session) {
    return <AuthLoadingState />;
  }

  return children;
}
