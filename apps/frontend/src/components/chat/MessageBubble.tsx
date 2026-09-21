"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { User, Sparkles, Copy, Check } from "lucide-react";

export interface MessageBubbleProps {
  role: "user" | "ai";
  content: string | React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function MessageBubble({ role, content, children, className }: MessageBubbleProps) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (typeof content === "string") {
      void navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        "group flex gap-[14px] animate-[msgSlideIn_0.32s_cubic-bezier(0.16,1,0.3,1)_both]",
        className
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-[30px] h-[30px] rounded-[10px] shrink-0 flex items-center justify-center transition-all duration-300",
          isUser
            ? "bg-white/[0.04] border border-glass-border text-cyan shadow-[0_0_10px_rgba(79,216,255,0.12)] group-hover:border-cyan/40"
            : "bg-gradient-to-br from-signal-400 via-signal-500 to-cyan text-white shadow-[0_0_14px_rgba(20,119,245,0.35)] group-hover:shadow-[0_0_18px_rgba(79,216,255,0.45)]"
        )}
      >
        {isUser ? (
          <User className="w-[15px] h-[15px]" />
        ) : (
          <Sparkles className="w-[15px] h-[15px]" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-[6px]">
          <div className="flex items-center gap-[8px]">
            <span className="font-mono text-[12px] text-text-dim group-hover:text-text-mid transition-colors">
              {isUser ? "You" : "WEBISCRAP"}
            </span>
            {!isUser && (
              <span className="font-mono text-[10px] text-cyan/90 bg-cyan/10 px-[6px] py-[1px] rounded-pill border border-cyan/20">
                Agent Swarm
              </span>
            )}
          </div>

          {typeof content === "string" && (
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-[4px] text-text-dim hover:text-text-hi rounded hover:bg-white/5 cursor-pointer"
              title="Copy message"
              aria-label="Copy message"
            >
              {copied ? (
                <Check className="w-[13px] h-[13px] text-success" />
              ) : (
                <Copy className="w-[13px] h-[13px]" />
              )}
            </button>
          )}
        </div>

        {isUser ? (
          <div className="p-[12px_16px] rounded-[16px] rounded-tl-sm bg-panel border border-glass-border/60 hover:border-glass-border transition-colors shadow-sm">
            {typeof content === "string" ? (
              <div className="text-[14.5px] leading-[1.65] text-text-hi whitespace-pre-wrap break-words">
                {content}
              </div>
            ) : (
              content
            )}
          </div>
        ) : typeof content === "string" ? (
          <div className="text-[14.5px] leading-[1.65] text-text-hi whitespace-pre-wrap break-words">
            {content}
          </div>
        ) : (
          content
        )}

        {children && <div className="mt-[14px]">{children}</div>}
      </div>
    </div>
  );
}
