"use client";

import Link from "next/link";
import { Menu, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { APP_NAME, navItems } from "@/lib/constants";

export function Navbar({ onOpenNavigation }: { onOpenNavigation: () => void }) {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open navigation" onClick={onOpenNavigation}>
          <Menu aria-hidden="true" />
        </Button>
        <Link href="/dashboard" className="text-base font-semibold text-primary-navy lg:hidden">
          {APP_NAME}
        </Link>
        <div className="hidden max-w-sm flex-1 items-center gap-2 rounded-md border border-border bg-background px-3 lg:flex">
          <Search aria-hidden="true" />
          <Input className="border-0 bg-transparent px-0 focus-visible:ring-0" placeholder="Search projects and reports" />
        </div>
        <nav className="ml-auto hidden items-center gap-1 md:flex lg:hidden">
          {navItems.map((item) => (
            <Button key={item.href} asChild variant="ghost" size="sm">
              <Link href={item.href}>{item.label}</Link>
            </Button>
          ))}
        </nav>
        <Button asChild className="ml-auto md:ml-0" size="sm">
          <Link href="/projects/new">New Project</Link>
        </Button>
      </div>
    </header>
  );
}
