"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Home, LibraryBig, Settings, X } from "lucide-react";
import { useEffect } from "react";

import { APP_NAME, navItems } from "@/lib/constants";
import { cn } from "@/lib/utils";

const icons = {
  Dashboard: Home,
  Projects: LibraryBig,
  Reports: FileText,
  Settings: Settings
};

export function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-border bg-primary-navy text-white lg:block">
      <SidebarContent />
    </aside>
  );
}

export function MobileSidebar({
  open,
  onOpenChange
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  useEffect(() => {
    if (!open) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    }

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onOpenChange]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
      <button
        type="button"
        aria-label="Close navigation"
        className="absolute inset-0 bg-foreground/40"
        onClick={() => onOpenChange(false)}
      />
      <aside className="relative flex h-full w-[min(20rem,calc(100vw-3rem))] flex-col border-r border-white/10 bg-primary-navy text-white shadow-lg">
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-5">
          <Link href="/dashboard" className="text-lg font-semibold" onClick={() => onOpenChange(false)}>
            {APP_NAME}
          </Link>
          <button
            type="button"
            aria-label="Close navigation"
            className="rounded-md p-2 text-white/75 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60"
            onClick={() => onOpenChange(false)}
          >
            <X className="size-5" aria-hidden="true" />
          </button>
        </div>
        <SidebarContent onNavigate={() => onOpenChange(false)} hideBrand />
      </aside>
    </div>
  );
}

function SidebarContent({
  onNavigate,
  hideBrand = false
}: {
  onNavigate?: () => void;
  hideBrand?: boolean;
}) {
  const pathname = usePathname();

  return (
    <>
      {hideBrand ? null : (
        <div className="flex h-16 items-center border-b border-white/10 px-6">
          <Link href="/dashboard" className="text-lg font-semibold">
            {APP_NAME}
          </Link>
        </div>
      )}
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const Icon = icons[item.label];
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-white/75 transition-colors hover:bg-white/10 hover:text-white",
                active && "bg-white/14 text-white"
              )}
            >
              <Icon aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </>
  );
}
