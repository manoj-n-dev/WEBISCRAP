import React from "react";
import { cn } from "@/lib/utils";

export interface LogoProps extends React.SVGProps<SVGSVGElement> {
  variant?: "mark" | "lockup";
  size?: number;
}

export function Logo({ variant = "lockup", size = 26, className, ...props }: LogoProps) {
  const isLockup = variant === "lockup";

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 56 56"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        {...props}
      >
        <path
          d="M6 16 L20 44 L28 26 L36 44 L50 16"
          stroke="url(#gnav)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Full mark includes the browser/download dots from the splash */}
        <path
          d="M28 8 v14 M22 14 v6 M34 14 v6"
          stroke="url(#gnav)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <defs>
          <linearGradient id="gnav" x1="6" y1="16" x2="50" y2="44">
            <stop stopColor="var(--color-signal-300)" />
            <stop offset="1" stopColor="var(--color-signal-500)" />
          </linearGradient>
        </defs>
      </svg>
      {isLockup && (
        <span className="font-display font-semibold text-[17px] tracking-[0.01em]">
          WEBISCRAP
        </span>
      )}
    </div>
  );
}
