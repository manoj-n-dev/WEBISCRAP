"use client";

import React, { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Hourglass, RefreshCw } from "lucide-react";

export interface LimitReachedProps {
  retryAfter?: number;          // seconds
  scope?: string;               // "minute" | "day"
  onRetry?: () => void;
  className?: string;
}

function fmt(seconds: number) {
  if (seconds >= 3600) return `${Math.ceil(seconds / 3600)} h`;
  if (seconds >= 60) return `${Math.ceil(seconds / 60)} min`;
  return `${seconds}s`;
}

/** Shown when the AI provider (Groq) rate limit is hit. Used inline in chat and by the /limit page. */
export function LimitReached({ retryAfter, scope, onRetry, className }: LimitReachedProps) {
  const [left, setLeft] = useState<number>(Math.max(0, Math.round(retryAfter ?? 0)));

  useEffect(() => {
    if (left <= 0) return;
    const t = setInterval(() => setLeft((s) => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [left]);

  const isDaily = scope === "day";
  return (
    <Card variant="strong" className={className ?? "p-[20px] sm:p-[24px]"} role="alert">
      <div className="flex items-start gap-[14px]">
        <div className="w-[40px] h-[40px] rounded-[12px] bg-[rgba(251,191,36,0.12)] text-warn flex items-center justify-center shrink-0">
          <Hourglass className="w-[20px] h-[20px]" />
        </div>
        <div className="min-w-0">
          <h3 className="text-[16px] font-semibold text-text-hi">AI usage limit reached</h3>
          <p className="mt-[6px] text-[13.5px] leading-[1.6] text-text-mid">
            {isDaily
              ? "The AI provider's daily quota for this app has been used up. It resets on its own — please try again later today."
              : "Too many AI requests were made in a short time. Your data and chat are safe; this clears automatically in a moment."}
          </p>
          {left > 0 && <p className="mt-[8px] font-mono text-[12px] text-cyan">Try again in about {fmt(left)}</p>}
          <div className="mt-[14px] flex flex-wrap gap-[10px]">
            {onRetry && (
              <Button variant="primary" onClick={onRetry} disabled={left > 0 && !isDaily && left > 5} className="text-[13px] py-[9px]">
                <RefreshCw className="w-[15px] h-[15px]" />
                Try again
              </Button>
            )}
          </div>
          <p className="mt-[12px] text-[11.5px] text-text-dim">
            Tip: shorter pages and smaller files use fewer AI tokens. Follow-up questions about data you already extracted are cheap.
          </p>
        </div>
      </div>
    </Card>
  );
}
