import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Table, Download, Maximize2 } from "lucide-react";

export interface DataCardProps {
  rows: number;
  cols: number;
  data: Record<string, any>[];
  totalRows?: number;
  cached?: boolean;
  className?: string;
}

export function DataCard({
  rows,
  cols,
  data,
  totalRows = rows,
  cached = false,
  className,
}: DataCardProps) {
  if (!data || data.length === 0) return null;
  const headers = Object.keys(data[0]);

  return (
    <Card variant="strong" className={cn("p-0 overflow-hidden", className)}>
      <div className="flex items-center justify-between p-[12px_16px] border-b border-hair">
        <div className="text-[13px] font-medium flex items-center gap-[8px] text-text-hi">
          <Table className="w-[15px] h-[15px]" />
          {totalRows} rows · {cols} columns
        </div>
        <div className="flex gap-[8px]">
          <Button variant="icon">
            <Download className="w-[15px] h-[15px]" />
          </Button>
          <Button variant="icon">
            <Maximize2 className="w-[15px] h-[15px]" />
          </Button>
        </div>
      </div>

      <div className="w-full overflow-x-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr>
              {headers.map((h, i) => (
                <th
                  key={i}
                  className="text-left font-mono text-[10.5px] text-text-dim uppercase tracking-[0.04em] p-[9px_16px] bg-white/2"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 5).map((row, i) => (
              <tr key={i} className="group">
                {headers.map((h, j) => (
                  <td
                    key={j}
                    className="p-[10px_16px] border-t border-hair text-text-mid group-hover:bg-[rgba(255,255,255,0.015)] group-hover:text-text-hi transition-colors"
                  >
                    {String(row[h])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between p-[10px_16px] border-t border-hair text-[12px] text-text-dim">
        <span>
          Showing {Math.min(5, data.length)} of {totalRows}{" "}
          {cached && "· cached for this session"}
        </span>
        <div className="flex gap-[6px]">
          <Chip className="cursor-pointer hover:border-signal-300 hover:text-text-hi">CSV</Chip>
          <Chip className="cursor-pointer hover:border-signal-300 hover:text-text-hi">Excel</Chip>
          <Chip className="cursor-pointer hover:border-signal-300 hover:text-text-hi">JSON</Chip>
          <Chip className="cursor-pointer hover:border-signal-300 hover:text-text-hi">PDF</Chip>
        </div>
      </div>
    </Card>
  );
}
