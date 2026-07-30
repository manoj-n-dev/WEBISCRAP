"use client";

import { useState, useRef, useEffect } from "react";
import { Link, ArrowUp, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string, url?: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [url, setUrl] = useState("");
  const [showUrl, setShowUrl] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 150) + "px";
    }
  }, [message]);

  const handleSubmit = () => {
    if (!message.trim() || isLoading) return;
    onSend(message.trim(), url.trim() || undefined);
    setMessage("");
    setUrl("");
    setShowUrl(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border px-4 py-4 bg-background flex justify-center">
      <div className="w-full max-w-3xl">
        {/* URL input */}
        {showUrl && (
          <div className="mb-2 animate-fade-in">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface border border-border">
              <Link className="w-4 h-4 text-muted shrink-0" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted outline-none"
              />
              <button
                onClick={() => { setShowUrl(false); setUrl(""); }}
                className="text-muted hover:text-foreground transition-colors text-xs cursor-pointer"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        {/* Message input */}
        <div className="flex items-end gap-2 px-4 py-3 rounded-2xl bg-surface border border-border focus-within:border-[#555]  transition-colors">
          {!showUrl && (
            <button
              onClick={() => setShowUrl(true)}
              className="shrink-0 mb-0.5 p-1 rounded-md text-muted hover:text-foreground transition-colors cursor-pointer"
              title="Attach URL"
            >
              <Link className="w-5 h-5" />
            </button>
          )}

          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message WEBISCRAP..."
            rows={1}
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted outline-none resize-none max-h-36 leading-relaxed"
            disabled={isLoading}
          />

          <button
            onClick={handleSubmit}
            disabled={!message.trim() || isLoading}
            className="shrink-0 w-8 h-8 rounded-lg bg-foreground disabled:bg-[#555] flex items-center justify-center transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 text-background animate-spin-slow" />
            ) : (
              <ArrowUp className="w-4 h-4 text-background" />
            )}
          </button>
        </div>

        <p className="text-[11px] text-center text-muted mt-2">
          WEBISCRAP uses AI to extract structured data from websites. Results may vary.
        </p>
      </div>
    </div>
  );
}
