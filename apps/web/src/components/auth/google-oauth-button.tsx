"use client";

import { Chrome } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { getSupabaseClient } from "@/lib/supabase-client";

export function GoogleOAuthButton() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const { toast } = useToast();

  async function continueWithGoogle() {
    setErrorMessage(null);
    setIsRedirecting(true);

    const supabase = getSupabaseClient();
    const redirectTo = `${window.location.origin}/auth/callback`;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo
      }
    });

    if (error) {
      setIsRedirecting(false);
      const message = "Could not start Google login. Try again.";
      setErrorMessage(message);
      toast({ title: "Google login failed", description: message, variant: "error" });
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <Button type="button" variant="outline" onClick={continueWithGoogle} disabled={isRedirecting}>
        <Chrome data-icon="inline-start" aria-hidden="true" />
        {isRedirecting ? "Opening Google" : "Continue with Google"}
      </Button>
      {errorMessage ? <p className="text-sm text-danger">{errorMessage}</p> : null}
    </div>
  );
}
