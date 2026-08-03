import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: "default" | "primary" | "ghost" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";

    const baseStyles =
      "inline-flex items-center justify-center gap-2 font-body font-medium text-[14px] transition-all cursor-pointer";
    
    const variants = {
      default:
        "px-[20px] py-[11px] rounded-pill border border-glass-border-strong text-text-hi bg-white/5 hover:bg-[rgba(130,170,255,0.08)] hover:border-signal-300 active:scale-98",
      primary:
        "px-[20px] py-[11px] rounded-pill border border-[rgba(130,190,255,0.5)] text-white bg-gradient-to-b from-signal-400 to-signal-500 shadow-[0_0_0_1px_rgba(20,119,245,0.25),0_8px_24px_rgba(20,119,245,0.35)] hover:brightness-110 active:scale-98",
      ghost:
        "px-[20px] py-[11px] rounded-pill border border-hair bg-transparent text-text-mid hover:bg-[rgba(130,170,255,0.08)] hover:border-signal-300 hover:text-text-hi active:scale-98",
      icon:
        "w-[28px] h-[28px] rounded-[7px] border border-hair flex items-center justify-center text-text-mid hover:border-glass-border-strong hover:text-text-hi transition-colors",
    };

    return (
      <Comp
        className={cn(baseStyles, variants[variant], className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
