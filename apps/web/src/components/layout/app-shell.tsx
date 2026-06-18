"use client";

import { useState } from "react";

import { Navbar } from "@/components/layout/navbar";
import { MobileSidebar, Sidebar } from "@/components/layout/sidebar";
import { AuthGuard } from "@/components/auth/auth-guard";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background">
        <div className="flex min-h-screen">
          <Sidebar />
          <MobileSidebar open={isMobileNavOpen} onOpenChange={setIsMobileNavOpen} />
          <div className="flex min-w-0 flex-1 flex-col">
            <Navbar onOpenNavigation={() => setIsMobileNavOpen(true)} />
            <main className="mx-auto w-full max-w-7xl flex-1 overflow-x-hidden px-4 py-6 sm:px-6 lg:px-8">{children}</main>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
