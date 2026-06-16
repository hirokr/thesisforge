"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Home, LibraryBig, Settings } from "lucide-react";

import { APP_NAME, navItems } from "@/lib/constants";
import { cn } from "@/lib/utils";

const icons = {
  Dashboard: Home,
  Projects: LibraryBig,
  Reports: FileText,
  Settings: Settings
};

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-border bg-primary-navy text-white lg:block">
      <div className="flex h-16 items-center border-b border-white/10 px-6">
        <Link href="/dashboard" className="text-lg font-semibold">
          {APP_NAME}
        </Link>
      </div>
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const Icon = icons[item.label];
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
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
    </aside>
  );
}
