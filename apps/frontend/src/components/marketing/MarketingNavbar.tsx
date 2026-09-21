"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";
import { Menu, X, ArrowRight } from "lucide-react";

const NAV_LINKS = [
  { href: "/how-it-works", label: "How It Works" },
  { href: "/features", label: "Features" },
  { href: "/agents", label: "Agents" },
  { href: "/docs", label: "Docs" },
  { href: "/creators", label: "Creators" },
];

export function MarketingNavbar() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Close drawer on route change / resize
  useEffect(() => {
    const close = () => setDrawerOpen(false);
    window.addEventListener("resize", close);
    return () => window.removeEventListener("resize", close);
  }, []);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 h-[64px] sm:h-[72px] flex items-center justify-between gap-[12px] px-[16px] sm:px-[32px] border-b border-[rgba(255,255,255,0.04)] bg-[rgba(5,7,12,0.7)] backdrop-blur-md z-50">
        <Link href="/" aria-label="WEBISCRAP home" onClick={() => setDrawerOpen(false)}>
          <Logo variant="lockup" size={24} />
        </Link>

        {/* Desktop nav links */}
        <div className="hidden md:flex items-center gap-[28px] text-[13px] font-medium text-text-mid">
          {NAV_LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-text-hi transition-colors">
              {l.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-[8px] sm:gap-[16px]">
          {/* Desktop CTA */}
          <Link href="/login" className="hidden sm:block">
            <Button variant="ghost" className="px-[20px] py-[11px] text-[14px]">
              Sign In
            </Button>
          </Link>
          <Link href="/login" className="hidden sm:block">
            <Button variant="primary" className="px-[20px] py-[11px] text-[14px]">
              Start Extracting
            </Button>
          </Link>

          {/* Mobile CTA (compact) */}
          <Link href="/login" className="sm:hidden">
            <Button variant="primary" className="px-[14px] py-[9px] text-[13px]">
              Start
            </Button>
          </Link>

          {/* Hamburger button */}
          <button
            onClick={() => setDrawerOpen((v) => !v)}
            className="md:hidden w-[40px] h-[40px] flex items-center justify-center rounded-lg border border-hair bg-white/5 hover:bg-white/10 text-text-mid hover:text-text-hi transition-colors cursor-pointer"
            aria-label={drawerOpen ? "Close menu" : "Open menu"}
            aria-expanded={drawerOpen}
          >
            {drawerOpen ? <X className="w-[18px] h-[18px]" /> : <Menu className="w-[18px] h-[18px]" />}
          </button>
        </div>
      </nav>

      {/* Mobile drawer backdrop */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm md:hidden"
          onClick={() => setDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile drawer */}
      <div
        className={`fixed top-[64px] left-0 right-0 z-40 md:hidden bg-[rgba(5,7,12,0.97)] border-b border-hair transition-all duration-300 ease-out overflow-hidden ${
          drawerOpen ? "max-h-[calc(100dvh-64px)] opacity-100" : "max-h-0 opacity-0 pointer-events-none"
        }`}
        aria-hidden={!drawerOpen}
      >
        <div className="flex flex-col p-[20px] gap-[6px]">
          {NAV_LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={() => setDrawerOpen(false)}
              className="flex items-center justify-between px-[16px] py-[14px] rounded-xl text-[15px] font-medium text-text-mid hover:text-text-hi hover:bg-white/[0.06] transition-colors border border-transparent hover:border-hair"
            >
              {l.label}
              <ArrowRight className="w-[14px] h-[14px] opacity-40" />
            </Link>
          ))}

          {/* Divider */}
          <div className="my-[8px] border-t border-hair" />

          {/* Auth CTAs */}
          <Link href="/login" onClick={() => setDrawerOpen(false)}>
            <Button variant="ghost" className="w-full justify-center py-[14px] text-[14px]">
              Sign In
            </Button>
          </Link>
          <Link href="/login" onClick={() => setDrawerOpen(false)}>
            <Button variant="primary" className="w-full justify-center py-[14px] text-[14px]">
              Start Extracting Free
            </Button>
          </Link>
        </div>
      </div>
    </>
  );
}
