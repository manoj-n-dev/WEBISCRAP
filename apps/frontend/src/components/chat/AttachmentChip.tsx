import React from "react";
import { cn } from "@/lib/utils";
import { FileText, FileSpreadsheet, Image as ImageIcon, Loader2, X, AlertCircle } from "lucide-react";
import type { Attachment } from "@/lib/store/chat";

function iconFor(name: string) {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "csv" || ext === "xlsx" || ext === "xls") return FileSpreadsheet;
  if (ext === "png" || ext === "jpg" || ext === "jpeg") return ImageIcon;
  return FileText;
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function AttachmentChip({ attachment, onRemove, className }: { attachment: Attachment; onRemove?: () => void; className?: string }) {
  const Icon = iconFor(attachment.name);
  const isError = attachment.status === "error";
  return (
    <div
      className={cn(
        "flex items-center gap-[10px] max-w-full sm:max-w-[280px] rounded-[10px] border px-[10px] py-[8px] bg-white/5",
        isError ? "border-red-500/40" : "border-glass-border",
        className,
      )}
    >
      <div className={cn("w-[30px] h-[30px] rounded-[8px] flex items-center justify-center shrink-0", isError ? "bg-red-500/10 text-red-400" : "bg-[rgba(20,119,245,0.12)] text-signal-400")}>
        {attachment.status === "uploading" ? <Loader2 className="w-[15px] h-[15px] animate-spin" /> : isError ? <AlertCircle className="w-[15px] h-[15px]" /> : <Icon className="w-[15px] h-[15px]" />}
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-[12.5px] text-text-hi truncate" title={attachment.name}>{attachment.name}</div>
        <div className={cn("text-[11px] truncate", isError ? "text-red-400" : "text-text-dim")}>
          {isError ? attachment.error : attachment.status === "uploading" ? "Uploading…" : `${formatSize(attachment.size)}${attachment.rows ? ` · ${attachment.rows} rows` : ""}`}
        </div>
      </div>
      {onRemove && (
        <button type="button" onClick={onRemove} aria-label={`Remove ${attachment.name}`} className="shrink-0 w-[24px] h-[24px] rounded-full flex items-center justify-center text-text-dim hover:text-text-hi hover:bg-white/10 cursor-pointer">
          <X className="w-[14px] h-[14px]" />
        </button>
      )}
    </div>
  );
}
