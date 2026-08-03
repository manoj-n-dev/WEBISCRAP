import React from "react";
import { cn } from "@/lib/utils";
import { User, Sparkles } from "lucide-react";

export interface MessageBubbleProps {
  role: "user" | "ai";
  content: string | React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function MessageBubble({ role, content, children, className }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("flex gap-[14px]", className)}>
      <div
        className={cn(
          "w-[28px] h-[28px] rounded-[9px] shrink-0 flex items-center justify-center",
          isUser
            ? "bg-white/5 text-text-dim"
            : "bg-gradient-to-br from-signal-400 to-signal-500 text-white"
        )}
      >
        {isUser ? (
          <User className="w-[15px] h-[15px]" />
        ) : (
          <Sparkles className="w-[15px] h-[15px]" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="font-mono text-[12px] text-text-dim mb-[6px]">
          {isUser ? "You" : "WEBISCRAP"}
        </div>
        
        {typeof content === "string" ? (
          <div className="text-[14.5px] leading-[1.65] text-text-hi">
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
