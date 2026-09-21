import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";

export function MarketingNavbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 h-[64px] sm:h-[72px] flex items-center justify-between gap-[12px] px-[16px] sm:px-[32px] border-b border-[rgba(255,255,255,0.04)] bg-[rgba(5,7,12,0.7)] backdrop-blur-md z-50">
      <Link href="/" aria-label="WEBISCRAP home">
        <Logo variant="lockup" size={24} />
      </Link>

      <div className="hidden md:flex items-center gap-[28px] text-[13px] font-medium text-text-mid">
        <Link href="/how-it-works" className="hover:text-text-hi transition-colors">
          How It Works
        </Link>
        <Link href="/features" className="hover:text-text-hi transition-colors">
          Features
        </Link>
        <Link href="/agents" className="hover:text-text-hi transition-colors">
          Agents
        </Link>
        <Link href="/docs" className="hover:text-text-hi transition-colors">
          Docs
        </Link>
        <Link href="/creators" className="hover:text-text-hi transition-colors">
          Creators
        </Link>
      </div>

      <div className="flex items-center gap-[8px] sm:gap-[16px]">
        <Link href="/login">
          <Button variant="ghost" className="px-[14px] py-[9px] sm:px-[20px] sm:py-[11px] text-[13px] sm:text-[14px]">
            Sign In
          </Button>
        </Link>
        <Link href="/login">
          <Button variant="primary" className="px-[14px] py-[9px] sm:px-[20px] sm:py-[11px] text-[13px] sm:text-[14px]">
            <span className="sm:hidden">Start</span>
            <span className="hidden sm:inline">Start Extracting</span>
          </Button>
        </Link>
      </div>
    </nav>
  );
}
