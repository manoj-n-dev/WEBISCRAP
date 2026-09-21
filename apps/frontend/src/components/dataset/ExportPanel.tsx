"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { FileText, FileSpreadsheet, FileJson, FileCode, Download, Loader2 } from "lucide-react";
import { exportSession, type ExportFormat } from "@/lib/export";

export interface ExportPanelProps {
  className?: string;
  sessionId?: string;
}

const formats = [
  { id: "csv", label: "CSV", icon: FileText, desc: "Opens in Excel · UTF-8" },
  { id: "excel", label: "Excel", icon: FileSpreadsheet, desc: ".xlsx workbook" },
  { id: "json", label: "JSON", icon: FileJson, desc: "For developers" },
  { id: "md", label: "Markdown", icon: FileCode, desc: "Table format" },
  { id: "pdf", label: "PDF", icon: FileText, desc: "Print ready (Latin text)" },
] as const;

export function ExportPanel({ className, sessionId }: ExportPanelProps) {
  const [busy, setBusy] = useState<ExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: ExportFormat) => {
    if (!sessionId || busy) return;
    setBusy(format);
    setError(null);
    try {
      await exportSession(format, sessionId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed. Please try again.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <Card variant="strong" className={cn("p-[16px] w-full lg:w-[280px] lg:shrink-0", className)}>
      <div className="font-mono text-[11px] text-text-dim uppercase tracking-[0.06em] mb-[12px]">Export As</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-[8px]">
        {formats.map((fmt) => (
          <button
            key={fmt.id}
            onClick={() => handleExport(fmt.id)}
            disabled={!sessionId || !!busy}
            className="flex items-center gap-[12px] p-[10px_12px] rounded-md bg-white/5 hover:bg-[rgba(130,170,255,0.08)] border border-transparent hover:border-signal-300 transition-all group text-left cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="w-[32px] h-[32px] rounded bg-[rgba(20,119,245,0.1)] flex items-center justify-center text-signal-400 group-hover:bg-signal-500 group-hover:text-white transition-colors shrink-0">
              <fmt.icon className="w-[16px] h-[16px]" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[13.5px] font-medium text-text-hi">{fmt.label}</div>
              <div className="text-[11px] text-text-dim truncate">{fmt.desc}</div>
            </div>
            {busy === fmt.id ? (
              <Loader2 className="w-[14px] h-[14px] animate-spin text-text-dim" />
            ) : (
              <Download className="w-[14px] h-[14px] text-text-dim lg:opacity-0 group-hover:opacity-100 transition-opacity" />
            )}
          </button>
        ))}
      </div>
      {error && <p role="alert" className="mt-[10px] text-[12px] text-red-400">{error}</p>}
    </Card>
  );
}
