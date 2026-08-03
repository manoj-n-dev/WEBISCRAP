import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";

export type AgentStep = "plan" | "analyze" | "browse" | "extract" | "clean" | "validate";

export interface PipelineStripProps {
  activeStep?: AgentStep;
  completedSteps?: AgentStep[];
  title?: string;
  className?: string;
}

const STEPS: AgentStep[] = ["plan", "analyze", "browse", "extract", "clean", "validate"];

export function PipelineStrip({
  activeStep,
  completedSteps = [],
  title = "Pipeline running...",
  className,
}: PipelineStripProps) {
  return (
    <Card className={cn("mt-[10px] mb-[6px] py-[14px] px-[16px]", className)}>
      <div className="font-mono text-[10.5px] tracking-[0.1em] text-text-dim uppercase mb-[12px]">
        {title}
      </div>
      <div className="flex items-center">
        {STEPS.map((step, index) => {
          const isDone = completedSteps.includes(step);
          const isActive = step === activeStep;
          const isLast = index === STEPS.length - 1;

          return (
            <div
              key={step}
              className={cn(
                "flex flex-col items-center gap-[6px] flex-1 relative",
                isDone && "done",
                isActive && "active"
              )}
            >
              {/* Line connector */}
              {!isLast && (
                <div
                  className={cn(
                    "absolute top-[5px] left-1/2 w-full h-[2px] z-0",
                    isDone ? "bg-[rgba(52,211,153,0.35)]" : "bg-hair"
                  )}
                />
              )}

              {/* Dot */}
              <div
                className={cn(
                  "w-[11px] h-[11px] rounded-full border-2 border-glass-border-strong bg-bg-1 z-10 transition-colors duration-300",
                  isDone && "bg-success border-success shadow-[0_0_8px_rgba(52,211,153,0.5)]",
                  isActive &&
                    "bg-cyan border-cyan shadow-[0_0_10px_rgba(79,216,255,0.6)] animate-[pulseDot_1.2s_ease-in-out_infinite]"
                )}
              />

              {/* Label */}
              <div
                className={cn(
                  "font-mono text-[9.5px] text-text-dim transition-colors",
                  (isDone || isActive) && "text-text-mid"
                )}
              >
                {step}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
