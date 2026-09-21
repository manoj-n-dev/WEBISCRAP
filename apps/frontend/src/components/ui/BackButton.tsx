"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BackButtonProps {
  fallbackHref?: string;
  label?: string;
  className?: string;
  variant?: "pill" | "ghost" | "inline";
}

export function BackButton({
  fallbackHref = "/",
  label = "Back",
  className,
  variant = "pill",
}: BackButtonProps) {
  const router = useRouter();

  const handleBack = () => {
    if (typeof window !== "undefined" && window.history.length > 2) {
      router.back();
    } else {
      router.push(fallbackHref);
    }
  };

  if (variant === "inline") {
    return (
      <button
        onClick={handleBack}
        className={cn(
          "group inline-flex items-center gap-1.5 text-[13px] text-text-dim hover:text-cyan transition-colors cursor-pointer select-none",
          className
        )}
        aria-label={label}
      >
        <ArrowLeft className="w-[15px] h-[15px] transition-transform duration-200 group-hover:-translate-x-1 text-text-dim group-hover:text-cyan" />
        <span>{label}</span>
      </button>
    );
  }

  return (
    <button
      onClick={handleBack}
      className={cn(
        "group inline-flex items-center gap-2 px-3 py-1.5 rounded-pill border border-glass-border bg-white/[0.03] hover:bg-[rgba(130,170,255,0.08)] hover:border-signal-400/50 text-text-mid hover:text-text-hi font-body text-[12.5px] transition-all duration-200 cursor-pointer shadow-sm hover:shadow-[0_0_12px_rgba(79,216,255,0.15)] select-none",
        className
      )}
      aria-label={label}
    >
      <ArrowLeft className="w-[14px] h-[14px] transition-transform duration-200 group-hover:-translate-x-1 text-cyan" />
      <span>{label}</span>
    </button>
  );
}
