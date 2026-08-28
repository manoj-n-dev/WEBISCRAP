"use client";

import React, { useMemo } from "react";
import Link from "next/link";
import { ArrowLeft, Search, Filter, Database, Clock, ShieldAlert } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ConfidenceBar } from "@/components/dataset/ConfidenceBar";
import { DataTable } from "@/components/dataset/DataTable";
import { ExportPanel } from "@/components/dataset/ExportPanel";
import { ColumnDef } from "@tanstack/react-table";
import { useChatStore } from "@/lib/store/chat";
import { ApiClient } from "@/lib/api/client";

const generateColumns = (data: any[]): ColumnDef<any>[] => {
  if (!data || data.length === 0) return [];
  
  // M8: Union keys across all rows to handle heterogeneous data
  const allKeys = new Set<string>();
  data.forEach(row => Object.keys(row).forEach(k => allKeys.add(k)));
  
  // Exclude 'conf' from standard keys since we want a custom renderer for it
  allKeys.delete('conf');
  
  const cols: ColumnDef<any>[] = Array.from(allKeys).map(key => ({
    accessorKey: key,
    header: key.toUpperCase(),
  }));
  
  // Remove the fake per-row confidence if it doesn't exist
  if (data[0].conf !== undefined) {
    cols.push({
      accessorKey: "conf",
      header: "CONFIDENCE",
      cell: ({ row }) => <ConfidenceBar score={row.original.conf} />
    });
  }
  
  return cols;
};

export default function DatasetPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const resolvedParams = React.use(params);
  const sessionId = resolvedParams.sessionId;
  const { messages } = useChatStore();
  
  const [apiData, setApiData] = React.useState<any[] | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  // Find the last completed extraction in the store
  const lastExtraction = useMemo(() => {
    const aiMessages = messages.filter(m => m.role === "ai" && m.status === "completed" && m.data);
    return aiMessages[aiMessages.length - 1];
  }, [messages]);

  React.useEffect(() => {
    async function fetchData() {
      try {
        const data = await ApiClient.getSessionData(sessionId);
        setApiData(data.cleaned_data || data.extracted_data || (Array.isArray(data) ? data : []));
      } catch (err) {
        console.error("Failed to load session data:", err);
      } finally {
        setIsLoading(false);
      }
    }
    
    if (!lastExtraction?.data) {
      fetchData();
    } else {
      setIsLoading(false);
    }
  }, [sessionId, lastExtraction]);

  const rawData = lastExtraction?.data || apiData || [];
  const columns = useMemo(() => generateColumns(rawData), [rawData]);
  
  const totalRows = rawData.length;
  // Use the actual overall confidence score and flagged fields from the ValidatorAgent
  const avgConf = lastExtraction?.confidenceScore ?? (apiData ? (apiData as any).confidenceScore : 100);
  const flaggedCount = lastExtraction?.flaggedFields ?? (apiData ? (apiData as any).flaggedFields : 0);

  return (
    <div className="flex flex-col h-full bg-bg-0 text-text-hi font-body overflow-hidden">
      <div className="bg-field"></div>
      
      <div className="relative z-10 flex flex-col h-full overflow-hidden p-[24px]">
        {/* Top Header */}
        <div className="flex items-center justify-between mb-[24px] shrink-0">
          <div className="flex items-center gap-[16px]">
            <Link href={`/chat/${sessionId}`}>
              <Button variant="icon">
                <ArrowLeft className="w-[16px] h-[16px]" />
              </Button>
            </Link>
            <div>
              <div className="text-[20px] font-display font-semibold">
                Extraction Dataset
              </div>
              <div className="text-[13px] text-text-dim flex items-center gap-[8px]">
                <span>Session {sessionId}</span>
                <span className="w-[4px] h-[4px] bg-glass-border-strong rounded-full"></span>
                <span>Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-4 gap-[16px] mb-[24px] shrink-0">
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(130,170,255,0.08)] flex items-center justify-center text-text-mid">
              <Database className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">{totalRows}</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Total Rows</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(52,211,153,0.1)] flex items-center justify-center text-success">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">{avgConf}%</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Avg Confidence</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(245,181,68,0.1)] flex items-center justify-center text-warn">
              <ShieldAlert className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">{flaggedCount}</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Flagged Fields</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(79,216,255,0.1)] flex items-center justify-center text-cyan">
              <Clock className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">Live</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Pipeline Time</div>
            </div>
          </Card>
        </div>

        {/* Main Content Area */}
        <div className="flex gap-[24px] flex-1 overflow-hidden">
          {/* Table Area */}
          <Card className="flex-1 p-[16px] flex flex-col overflow-hidden">
            <div className="flex items-center gap-[12px] mb-[16px] shrink-0">
              <Input 
                icon={<Search className="w-[15px] h-[15px]" />}
                placeholder="Search extracted data..."
                className="max-w-[320px]"
              />
              <Button variant="ghost">
                <Filter className="w-[15px] h-[15px]" />
                Filter
              </Button>
            </div>
            
            <div className="flex-1 overflow-hidden">
              {totalRows > 0 ? (
                <DataTable columns={columns} data={rawData} />
              ) : (
                <div className="h-full flex items-center justify-center text-text-dim">
                  No data available. Run an extraction in the chat first.
                </div>
              )}
            </div>
          </Card>
          
          {/* Export Panel */}
          <ExportPanel 
            data={rawData}
            onExport={(fmt) => console.log(`Exporting as ${fmt}`)} 
            className="w-[280px] shrink-0" 
          />
        </div>
      </div>
    </div>
  );
}
