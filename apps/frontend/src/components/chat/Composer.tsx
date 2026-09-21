"use client";

import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Paperclip, ArrowUp, Loader2 } from "lucide-react";
import { AttachmentChip } from "@/components/chat/AttachmentChip";
import type { Attachment } from "@/lib/store/chat";
import { useSound } from "@/lib/useSound";

export interface ComposerProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: () => void;
  isLoading?: boolean;
  attachments?: Attachment[];
  onAttach?: (files: File[]) => void;
  onRemoveAttachment?: (id: string) => void;
}

export function Composer({ value, onChange, onSubmit, isLoading, attachments = [], onAttach, onRemoveAttachment }: ComposerProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const sound = useSound();

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }
  }, [value]);

  const uploading = attachments.some((a) => a.status === "uploading");
  const hasReady = attachments.some((a) => a.status === "ready");
  const canSend = !isLoading && !uploading && (value.trim().length > 0 || hasReady);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!e.ctrlKey && !e.altKey && !e.metaKey && (e.key.length === 1 || e.key === "Backspace" || e.key === "Delete")) {
      sound.playTyping();
    }
    // On phones Enter should insert a new line; the send button submits. Desktop keeps Enter-to-send.
    const isTouch = typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches;
    if (e.key === "Enter" && !e.shiftKey && !isTouch) {
      e.preventDefault();
      if (canSend) onSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length) {
      sound.play("upload");
      if (onAttach) onAttach(files);
    }
    e.target.value = "";          // allow re-selecting the same file
  };

  return (
    <div className="px-[12px] sm:px-[26px] pt-[10px] sm:pt-[16px] pb-[max(12px,env(safe-area-inset-bottom))] sm:pb-[22px]">
      <Card
        variant="strong"
        className="max-w-[760px] mx-auto p-[8px] transition-all duration-200 border-glass-border focus-within:border-cyan/50 focus-within:shadow-[0_0_24px_rgba(79,216,255,0.12)] focus-within:bg-panel-strong"
      >
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-[8px] p-[4px_4px_10px]">
            {attachments.map((a) => (
              <AttachmentChip key={a.id} attachment={a} onRemove={onRemoveAttachment ? () => onRemoveAttachment(a.id) : undefined} />
            ))}
          </div>
        )}
        <div className="flex items-end gap-[8px] sm:gap-[10px]">
          <input ref={fileInputRef} type="file" multiple accept=".pdf,.docx,.csv,.png,.jpg,.jpeg,.xlsx,.xls" className="hidden" onChange={handleFileChange} />
          <Button
            variant="icon"
            className="border-none self-end shrink-0 hover:text-cyan hover:scale-110 active:scale-95 transition-all duration-200"
            onClick={() => fileInputRef.current?.click()}
            aria-label="Attach a file"
            title="Attach a file (PDF, DOCX, CSV, Excel, image)"
          >
            <Paperclip className="w-[18px] h-[18px]" />
          </Button>

          <textarea
            ref={textareaRef}
            rows={1}
            placeholder="Paste a URL, attach a file, or ask a follow-up…"
            value={value}
            onChange={onChange}
            onKeyDown={handleKeyDown}
            enterKeyHint="send"
            className="flex-1 min-w-0 bg-transparent border-none outline-none resize-none text-text-hi font-body text-[16px] sm:text-[14px] leading-[1.5] py-[8px] max-h-[120px] placeholder:text-text-dim disabled:opacity-50"
            disabled={isLoading}
          />

          <button
            onClick={onSubmit}
            disabled={!canSend}
            aria-label={isLoading ? "Processing extraction" : "Send extraction request"}
            className={cn(
              "w-[38px] h-[38px] sm:w-[34px] sm:h-[34px] rounded-full bg-gradient-to-b from-signal-400 to-signal-500 flex items-center justify-center cursor-pointer shrink-0 self-end transition-all duration-200",
              canSend
                ? "shadow-[0_0_0_1px_rgba(130,190,255,0.4),0_6px_18px_rgba(20,119,245,0.45)] hover:scale-105 active:scale-95 hover:brightness-110"
                : "opacity-40 cursor-not-allowed shadow-none"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-[16px] h-[16px] text-white animate-spin" />
            ) : (
              <ArrowUp className="w-[16px] h-[16px] text-white stroke-2" />
            )}
          </button>
        </div>
      </Card>
      <div className="max-w-[760px] mx-auto mt-[8px] text-center text-[11px] text-text-dim">
        WEBISCRAP can misread dynamic pages — verify exported data before use.
      </div>
    </div>
  );
}
