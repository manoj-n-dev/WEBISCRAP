import * as React from "react";
import { cn } from "@/lib/utils";

export interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  dot?: "live" | "ok" | "warn" | "none";
}

const Chip = React.forwardRef<HTMLSpanElement, ChipProps>(
  ({ className, dot = "none", children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center gap-[6px] font-mono text-[11px] tracking-[0.04em] px-[10px] py-[5px] rounded-pill border border-glass-border text-text-mid bg-white/2 transition-colors",
          className
        )}
        {...props}
      >
        {dot !== "none" && (
          <span
            className={cn(
              "w-[6px] h-[6px] rounded-full",
              dot === "live" && "bg-cyan shadow-[0_0_8px_var(--color-cyan)]",
              dot === "ok" && "bg-success shadow-[0_0_8px_var(--color-success)]",
              dot === "warn" && "bg-warn"
            )}
          />
        )}
        {children}
      </span>
    );
  }
);
Chip.displayName = "Chip";

export { Chip };
