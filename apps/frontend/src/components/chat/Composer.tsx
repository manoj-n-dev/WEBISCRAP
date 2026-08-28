"use client";

import React, { useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Paperclip, Mic, MicOff, ArrowUp } from "lucide-react";
import { ApiClient } from "@/lib/api/client";

export interface ComposerProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: () => void;
  isLoading?: boolean;
}

export function Composer({ value, onChange, onSubmit, isLoading }: ComposerProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<any>(null);

  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  // H4: Wire paperclip to file upload
  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const result = await ApiClient.uploadFile(file);
      // Inject parsed preview into the textarea as context
      const preview = result.preview || "File uploaded successfully.";
      const syntheticEvent = {
        target: { value: value + (value ? "\n" : "") + `[Uploaded: ${file.name}]\n${preview}` },
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onChange(syntheticEvent);
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    }
    // Reset input so the same file can be re-selected
    e.target.value = "";
  };

  // H5: Wire mic button to Web Speech API
  const handleMicToggle = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Speech recognition is not supported in this browser. Try Chrome.");
      return;
    }

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      const syntheticEvent = {
        target: { value: value + (value ? " " : "") + transcript },
      } as React.ChangeEvent<HTMLTextAreaElement>;
      onChange(syntheticEvent);
      setIsRecording(false);
    };

    recognition.onerror = () => {
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  return (
    <div className="px-[26px] pb-[22px] pt-[16px]">
      <Card variant="strong" className="max-w-[760px] mx-auto p-[8px_8px_8px_18px] flex items-end gap-[10px]">
        {/* H4: Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.csv,.png,.jpg,.jpeg"
          className="hidden"
          onChange={handleFileChange}
        />
        <Button variant="icon" className="border-none self-end shrink-0" onClick={handleFileClick}>
          <Paperclip className="w-[18px] h-[18px]" />
        </Button>
        
        <textarea
          ref={textareaRef}
          rows={1}
          placeholder="Ask for anything — a URL, a follow-up, an export request…"
          value={value}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent border-none outline-none resize-none text-text-hi font-body text-[14px] leading-[1.5] py-[8px] max-h-[120px] placeholder:text-text-dim disabled:opacity-50"
          disabled={isLoading}
        />
        
        <div className="flex items-center gap-[6px] shrink-0 self-end">
          {/* H5: Voice input button */}
          <Button
            variant="icon"
            className={cn("border-none", isRecording && "text-red-500 animate-pulse")}
            onClick={handleMicToggle}
          >
            {isRecording ? (
              <MicOff className="w-[18px] h-[18px]" />
            ) : (
              <Mic className="w-[18px] h-[18px]" />
            )}
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
