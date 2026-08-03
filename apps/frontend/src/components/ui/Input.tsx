import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, icon, ...props }, ref) => {
    return (
      <div className="relative w-full">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim flex items-center justify-center">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            "flex w-full rounded-sm border border-hair bg-white/5 px-[14px] py-[12px] font-body text-[14px] text-text-hi transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-text-dim focus-visible:outline-none focus-visible:border-signal-400 focus-visible:shadow-[0_0_0_3px_rgba(20,119,245,0.15)] disabled:cursor-not-allowed disabled:opacity-50",
            icon && "pl-[38px]",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
