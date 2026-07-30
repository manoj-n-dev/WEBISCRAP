"use client";

import {
  ClipboardList,
  Search,
  Globe,
  PackageOpen,
  Eraser,
  ShieldCheck,
  Check,
  Loader2,
} from "lucide-react";
import type { AgentStep } from "@/app/page";

interface AgentProgressProps {
  steps: AgentStep[];
}

const agentIcons: Record<string, React.ElementType> = {
  planner: ClipboardList,
  analyzer: Search,
  browser: Globe,
  extractor: PackageOpen,
  cleaner: Eraser,
  validator: ShieldCheck,
};

export function AgentProgress({ steps }: AgentProgressProps) {
  const doneCount = steps.filter((s) => s.status === "done").length;
  const progress = Math.round((doneCount / steps.length) * 100);

  return (
    <div className="rounded-xl border border-border bg-surface p-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-foreground">
          Agent Pipeline
        </span>
        <span className="text-xs text-muted">
          {progress}% complete
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1 rounded-full bg-border mb-4 overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-1">
        {steps.map((step) => {
          const Icon = agentIcons[step.name] || ClipboardList;
          return (
            <div
              key={step.name}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs transition-colors ${
                step.status === "done"
                  ? "text-primary"
                  : step.status === "running"
                  ? "text-foreground bg-surface-hover"
                  : "text-muted"
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="flex-1">{step.label}</span>
              {step.status === "done" && <Check className="w-3.5 h-3.5" />}
              {step.status === "running" && <Loader2 className="w-3.5 h-3.5 animate-spin-slow" />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
