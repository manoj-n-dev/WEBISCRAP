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
  
  // Union keys across all rows to handle heterogeneous data
  const allKeys = new Set<string>();
  data.forEach(row => {
    if (row && typeof row === "object") {
      Object.keys(row).forEach(k => allKeys.add(k));
    }
  });
  
  // Exclude internal keys from standard columns
  allKeys.delete("conf");
  allKeys.delete("_flagged");
  
  const cols: ColumnDef<any>[] = Array.from(allKeys).map(key => ({
    id: key,
    accessorFn: (row: any) => row?.[key],
    header: key.replace(/_/g, " ").toUpperCase(),
    cell: ({ getValue }) => {
      const val = getValue();
      if (val === null || val === undefined) {
        return <span className="text-text-dim italic">—</span>;
      }
      if (typeof val === "object") {
        return <span className="font-mono text-[11px]">{JSON.stringify(val)}</span>;
      }
      return <span>{String(val)}</span>;
    },
  }));
  
  if (data.some(row => row && row.conf !== undefined)) {
    cols.push({
      id: "conf",
      accessorFn: (row: any) => row?.conf,
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
  
  const [apiResponse, setApiResponse] = React.useState<any>(null);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [flaggedOnly, setFlaggedOnly] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  // Find the last completed extraction in the store
  const lastExtraction = useMemo(() => {
    const aiMessages = messages.filter(m => m.role === "ai" && m.status === "completed" && m.data);
    return aiMessages[aiMessages.length - 1];
  }, [messages]);

  React.useEffect(() => {
    async function fetchData() {
      if (!sessionId || sessionId === "new") {
        setIsLoading(false);
        return;
      }
      try {
        setIsLoading(true);
        const data = await ApiClient.getSessionData(sessionId);
        setApiResponse(data);
      } catch (err) {
        console.error("Failed to load session data:", err);
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchData();
  }, [sessionId]);

  const rawData = useMemo(() => {
    if (apiResponse) {
      if (Array.isArray(apiResponse.cleaned_data) && apiResponse.cleaned_data.length > 0) {
        return apiResponse.cleaned_data;
      }
      if (Array.isArray(apiResponse.data?.cleaned_data) && apiResponse.data.cleaned_data.length > 0) {
        return apiResponse.data.cleaned_data;
      }
      if (Array.isArray(apiResponse.extracted_data) && apiResponse.extracted_data.length > 0) {
        return apiResponse.extracted_data;
      }
      if (Array.isArray(apiResponse.data?.extracted_data) && apiResponse.data.extracted_data.length > 0) {
        return apiResponse.data.extracted_data;
      }
      if (Array.isArray(apiResponse.data) && apiResponse.data.length > 0) {
        return apiResponse.data;
      }
      if (Array.isArray(apiResponse.result?.data) && apiResponse.result.data.length > 0) {
        return apiResponse.result.data;
      }
      if (Array.isArray(apiResponse) && apiResponse.length > 0) {
        return apiResponse;
      }
    }
    if (lastExtraction?.data && Array.isArray(lastExtraction.data) && lastExtraction.data.length > 0) {
      return lastExtraction.data;
    }
    return [];
  }, [apiResponse, lastExtraction]);

  // Filter rawData based on search query and optional flagged filter
  const filteredData = useMemo(() => {
    let result = rawData;
    if (flaggedOnly) {
      result = result.filter((row: any) => (row.conf !== undefined && row.conf < 90) || row._flagged);
    }
    if (!searchQuery.trim()) return result;
    const q = searchQuery.toLowerCase();
    return result.filter((row: any) =>
      Object.values(row).some((val) =>
        val !== null && val !== undefined && String(val).toLowerCase().includes(q)
      )
    );
  }, [rawData, searchQuery, flaggedOnly]);

  const columns = useMemo(() => generateColumns(rawData), [rawData]);
  
  const totalRows = rawData.length;
  const avgConf = (lastExtraction?.confidenceScore !== undefined && lastExtraction.confidenceScore !== null)
    ? lastExtraction.confidenceScore
    : (apiResponse?.validation?.confidence_score != null ? Math.round(apiResponse.validation.confidence_score) : 100);
  const flaggedCount = (lastExtraction?.flaggedFields !== undefined && lastExtraction.flaggedFields !== null)
    ? lastExtraction.flaggedFields
    : (apiResponse?.validation?.flagged_rows_count ?? (apiResponse?.validation?.flagged_fields?.length ?? 0));

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
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Button 
                variant={flaggedOnly ? "default" : "ghost"}
                onClick={() => setFlaggedOnly(!flaggedOnly)}
              >
                <Filter className="w-[15px] h-[15px]" />
                {flaggedOnly ? "Flagged Only" : "Filter"}
              </Button>
            </div>
            
            <div className="flex-1 overflow-hidden">
              {totalRows > 0 ? (
                <DataTable columns={columns} data={filteredData} />
              ) : (
                <div className="h-full flex items-center justify-center text-text-dim">
                  {isLoading ? "Loading session data..." : "No data available. Run an extraction in the chat first."}
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
