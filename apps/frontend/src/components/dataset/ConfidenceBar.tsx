import React from "react";
import { cn } from "@/lib/utils";

export interface ConfidenceBarProps {
  score: number; // 0 to 1
  className?: string;
}

export function ConfidenceBar({ score, className }: ConfidenceBarProps) {
  const percentage = Math.round(score * 100);
  const isHigh = score >= 0.8;
  const isMed = score >= 0.5 && score < 0.8;

  let colorClass = "bg-danger";
  let trackClass = "bg-[rgba(242,89,107,0.15)]";
  
  if (isHigh) {
    colorClass = "bg-success";
    trackClass = "bg-[rgba(52,211,153,0.15)]";
  } else if (isMed) {
    colorClass = "bg-warn";
    trackClass = "bg-[rgba(245,181,68,0.15)]";
  }

  return (
    <div className={cn("flex items-center gap-[8px]", className)}>
      <div className={cn("w-[34px] h-[4px] rounded-full overflow-hidden", trackClass)}>
        <div 
          className={cn("h-full rounded-full transition-all", colorClass)}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="font-mono text-[10.5px] text-text-dim">{percentage}%</span>
    </div>
  );
}
