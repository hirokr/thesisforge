import { createClient } from "@supabase/supabase-js";

import { readPublicEnv } from "@/lib/env";

let client: ReturnType<typeof createClient> | null = null;

export function getSupabaseClient() {
  client ??= createClient(
    readPublicEnv("NEXT_PUBLIC_SUPABASE_URL"),
    readPublicEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
    {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true
      }
    }
  );

  return client;
}
