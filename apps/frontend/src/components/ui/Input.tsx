import * as React from "react";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  rightElement?: React.ReactNode;
  showPasswordToggle?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, icon, rightElement, showPasswordToggle, ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);

    const isPassword = type === "password";
    const hasToggle = isPassword && (showPasswordToggle ?? true);
    const effectiveType = hasToggle && showPassword ? "text" : type;

    const hasRightContent = Boolean(rightElement || hasToggle);
    const hasBothRightActions = Boolean(rightElement && hasToggle);

    return (
      <div className="relative w-full">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim flex items-center justify-center">
            {icon}
          </div>
        )}
        <input
          type={effectiveType}
          className={cn(
            "flex w-full rounded-sm border border-hair bg-white/5 px-[14px] py-[12px] font-body text-[14px] text-text-hi transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-text-dim focus-visible:outline-none focus-visible:border-signal-400 focus-visible:shadow-[0_0_0_3px_rgba(20,119,245,0.15)] disabled:cursor-not-allowed disabled:opacity-50",
            icon && "pl-[38px]",
            hasBothRightActions ? "pr-[68px]" : hasRightContent ? "pr-[38px]" : "",
            className
          )}
          ref={ref}
          {...props}
        />
        {hasRightContent && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2 text-text-dim">
            {rightElement}
            {hasToggle && (
              <button
                type="button"
                tabIndex={-1}
                onClick={() => setShowPassword((prev) => !prev)}
                className="text-text-dim hover:text-text-hi transition-colors focus:outline-none flex items-center justify-center p-0.5 rounded hover:bg-white/5 cursor-pointer"
                aria-label={showPassword ? "Hide password" : "Show password"}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            )}
          </div>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
