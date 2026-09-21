import React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export interface LogoProps {
  variant?: "mark" | "lockup";
  size?: number;
  className?: string;
}

/** Brand mark (public/logo-mark.png, generated from public/assets/inner-logo.png) + wordmark. */
export function Logo({ variant = "lockup", size = 26, className }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Image src="/logo-mark.png" alt={variant === "mark" ? "WEBISCRAP" : ""} width={size} height={size} priority style={{ width: size, height: size }} />
      {variant === "lockup" && (
        <span className="font-display font-semibold text-[17px] tracking-[0.01em]">WEBISCRAP</span>
      )}
    </div>
  );
}
