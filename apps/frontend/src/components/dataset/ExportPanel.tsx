import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { FileText, FileSpreadsheet, FileJson, FileCode, Download } from "lucide-react";

export interface ExportPanelProps {
  className?: string;
  onExport: (format: "csv" | "excel" | "json" | "md" | "pdf") => void;
}

const formats = [
  { id: "csv", label: "CSV", icon: FileText, desc: "For spreadsheets" },
  { id: "excel", label: "Excel", icon: FileSpreadsheet, desc: ".xlsx format" },
  { id: "json", label: "JSON", icon: FileJson, desc: "For developers" },
  { id: "md", label: "Markdown", icon: FileCode, desc: "Table format" },
  { id: "pdf", label: "PDF", icon: FileText, desc: "Print ready" },
] as const;

export function ExportPanel({ className, onExport }: ExportPanelProps) {
  return (
    <Card variant="strong" className={cn("p-[16px] min-w-[280px]", className)}>
      <div className="font-mono text-[11px] text-text-dim uppercase tracking-[0.06em] mb-[12px]">
        Export As
      </div>
      
      <div className="flex flex-col gap-[8px]">
        {formats.map((fmt) => (
          <button
            key={fmt.id}
            onClick={() => onExport(fmt.id)}
            className="flex items-center gap-[12px] p-[10px_12px] rounded-md bg-white/5 hover:bg-[rgba(130,170,255,0.08)] border border-transparent hover:border-signal-300 transition-all group text-left cursor-pointer"
          >
            <div className="w-[32px] h-[32px] rounded bg-[rgba(20,119,245,0.1)] flex items-center justify-center text-signal-400 group-hover:bg-signal-500 group-hover:text-white transition-colors">
              <fmt.icon className="w-[16px] h-[16px]" />
            </div>
            <div className="flex-1">
              <div className="text-[13.5px] font-medium text-text-hi">{fmt.label}</div>
              <div className="text-[11px] text-text-dim">{fmt.desc}</div>
            </div>
            <Download className="w-[14px] h-[14px] text-text-dim opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        ))}
      </div>
    </Card>
  );
}
