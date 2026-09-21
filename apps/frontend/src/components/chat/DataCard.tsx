"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Table, Download, Maximize2, Check } from "lucide-react";
import { columnsOf, exportSession, formatCell, type ExportFormat } from "@/lib/export";
import { useRouter } from "next/navigation";

export interface DataCardProps {
  data: Record<string, any>[];
  totalRows?: number;
  label?: string;              // e.g. "Matching rows"
  previewRows?: number;
  showExports?: boolean;
  className?: string;
  sessionId?: string;
}

export function DataCard({ data, totalRows, label, previewRows = 5, showExports = true, className, sessionId }: DataCardProps) {
  const router = useRouter();
  const [busy, setBusy] = useState<ExportFormat | null>(null);
  const [success, setSuccess] = useState<ExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!data || data.length === 0) return null;
  const headers = columnsOf(data);
  const total = totalRows ?? data.length;

  const run = async (format: ExportFormat) => {
    if (!sessionId || busy) return;
    setBusy(format);
    setError(null);
    try {
      await exportSession(format, sessionId);
      setSuccess(format);
      setTimeout(() => setSuccess(null), 2500);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    } finally {
      setBusy(null);
    }
  };

  return (
    <Card variant="strong" className={cn("p-0 overflow-hidden", className)}>
      <div className="flex items-center justify-between gap-[8px] p-[12px_14px] sm:p-[12px_16px] border-b border-hair">
        <div className="text-[13px] font-medium flex items-center gap-[8px] text-text-hi min-w-0">
          <Table className="w-[15px] h-[15px] shrink-0" />
          <span className="truncate">{label ? `${label} · ` : ""}{total} rows · {headers.length} columns</span>
        </div>
        {sessionId && (
          <div className="flex gap-[8px] shrink-0">
            {showExports && (
              <Button variant="icon" onClick={() => run("csv")} title="Download CSV" aria-label="Download CSV">
                <Download className="w-[15px] h-[15px]" />
              </Button>
            )}
            <Button variant="icon" onClick={() => router.push(`/dataset/${sessionId}`)} title="Open in Dataset View" aria-label="Open in Dataset View">
              <Maximize2 className="w-[15px] h-[15px]" />
            </Button>
          </div>
        )}
      </div>

      <div className="w-full overflow-x-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr>
              {headers.map((h) => (
                <th key={h} className="text-left font-mono text-[10.5px] text-text-dim uppercase tracking-[0.04em] p-[9px_14px] bg-white/2 whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, previewRows).map((row, i) => (
              <tr key={i} className="group">
                {headers.map((h) => {
                  const text = formatCell(row[h]);
                  return (
                    <td key={h} className="p-[10px_14px] border-t border-hair text-text-mid group-hover:text-text-hi transition-colors max-w-[260px] truncate" title={text}>
                      {text === "" ? <span className="text-text-dim">—</span> : text}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-[8px] p-[10px_14px] sm:p-[10px_16px] border-t border-hair text-[12px] text-text-dim">
        <span>Showing {Math.min(previewRows, data.length)} of {total}</span>
        {showExports && sessionId && (
          <div className="flex flex-wrap gap-[6px]">
            {(["csv", "excel", "json", "md", "pdf"] as const).map((f) => (
              <Chip key={f} className="cursor-pointer hover:border-signal-300 hover:text-text-hi transition-colors" onClick={() => run(f)}>
                {busy === f ? (
                  "Exporting…"
                ) : success === f ? (
                  <span className="flex items-center gap-1 text-cyan font-mono">
                    <Check className="w-[11px] h-[11px]" />
                    Saved
                  </span>
                ) : f === "excel" ? (
                  "Excel"
                ) : f === "md" ? (
                  "Markdown"
                ) : (
                  f.toUpperCase()
                )}
              </Chip>
            ))}
          </div>
        )}
      </div>
      {error && <p role="alert" className="px-[16px] pb-[10px] text-[12px] text-red-400">{error}</p>}
    </Card>
  );
}
