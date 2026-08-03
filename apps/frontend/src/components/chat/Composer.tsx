import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Paperclip, Mic, ArrowUp } from "lucide-react";

export interface ComposerProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: () => void;
  isLoading?: boolean;
}

export function Composer({ value, onChange, onSubmit, isLoading }: ComposerProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="px-[26px] pb-[22px] pt-[16px]">
      <Card variant="strong" className="max-w-[760px] mx-auto p-[8px_8px_8px_18px] flex items-end gap-[10px]">
        <Button variant="icon" className="border-none self-end shrink-0">
          <Paperclip className="w-[18px] h-[18px]" />
        </Button>
        
        <textarea
          rows={1}
          placeholder="Ask for anything — a URL, a follow-up, an export request…"
          value={value}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent border-none outline-none resize-none text-text-hi font-body text-[14px] leading-[1.5] py-[8px] max-h-[120px] placeholder:text-text-dim disabled:opacity-50"
          disabled={isLoading}
        />
        
        <div className="flex items-center gap-[6px] shrink-0 self-end">
          <Button variant="icon" className="border-none">
            <Mic className="w-[18px] h-[18px]" />
          </Button>
          <button
            onClick={onSubmit}
            disabled={isLoading || !value.trim()}
            className="w-[34px] h-[34px] rounded-full bg-gradient-to-b from-signal-400 to-signal-500 flex items-center justify-center cursor-pointer shadow-[0_0_0_1px_rgba(130,190,255,0.4),0_6px_16px_rgba(20,119,245,0.35)] disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110 active:scale-95 transition-all"
          >
            <ArrowUp className="w-[16px] h-[16px] text-white stroke-2" />
          </button>
        </div>
      </Card>
      
      <div className="max-w-[760px] mx-auto mt-[8px] text-center text-[11px] text-text-dim">
        WEBISCRAP can misread dynamic pages — verify exported data before use.
      </div>
    </div>
  );
}
