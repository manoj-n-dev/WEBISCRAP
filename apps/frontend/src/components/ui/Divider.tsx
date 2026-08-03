import * as React from "react";
import { cn } from "@/lib/utils";

export interface DividerProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical";
}

const Divider = React.forwardRef<HTMLDivElement, DividerProps>(
  ({ className, orientation = "horizontal", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-hair",
          orientation === "horizontal" ? "h-[1px] w-full" : "w-[1px] h-full",
          className
        )}
        {...props}
      />
    );
  }
);
Divider.displayName = "Divider";

export { Divider };
