import React from "react";

/** Lightweight "answering" indicator for follow-up questions (no pipeline strip). */
export function ThinkingDots({ label = "Thinking" }: { label?: string }) {
  return (
    <div className="flex items-center gap-[8px] text-[13px] text-text-dim" aria-live="polite">
      <span className="flex gap-[4px]" aria-hidden>
        {[0, 1, 2].map((i) => (
          <span key={i} className="w-[6px] h-[6px] rounded-full bg-cyan animate-pulse" style={{ animationDelay: `${i * 0.18}s` }} />
        ))}
      </span>
      {label}…
    </div>
  );
}
