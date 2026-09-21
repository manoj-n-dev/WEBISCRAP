"use client";

import React, { useMemo } from "react";
import Link from "next/link";
import { ArrowLeft, Search, Filter, Database, Columns3, ShieldAlert } from "lucide-react";
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

export default function DatasetView({ sessionId }: { sessionId: string }) {
  const messages = useChatStore((s) => s.messages);
  
  const [apiResponse, setApiResponse] = React.useState<any>(null);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [flaggedOnly, setFlaggedOnly] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);

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
        setLoadError(null);
        const data = await ApiClient.getSessionData(sessionId);
        setApiResponse(data);
      } catch (err) {
        console.error("Failed to load session data:", err);
        setLoadError(err instanceof Error ? err.message : "Could not load this dataset.");
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
  
  const totalRows = apiResponse?.total_rows ?? rawData.length;
  const totalCols = columns.filter((c) => c.id !== "conf").length;
  const avgConf = (lastExtraction?.confidenceScore !== undefined && lastExtraction.confidenceScore !== null)
    ? lastExtraction.confidenceScore
    : (apiResponse?.validation?.confidence_score != null ? Math.round(apiResponse.validation.confidence_score) : 100);
  const flaggedCount = (lastExtraction?.flaggedFields !== undefined && lastExtraction.flaggedFields !== null)
    ? lastExtraction.flaggedFields
    : (apiResponse?.validation?.flagged_rows_count ?? (apiResponse?.validation?.flagged_fields?.length ?? 0));

  return (
    <div className="flex flex-col min-h-full lg:h-full bg-bg-0 text-text-hi font-body lg:overflow-hidden">
      <div className="bg-field"></div>
      
      <div className="relative z-10 flex flex-col lg:h-full lg:overflow-hidden p-[12px] sm:p-[24px]">
        {/* Top Header */}
        <div className="flex items-center justify-between mb-[16px] sm:mb-[24px] shrink-0">
          <div className="flex items-center gap-[16px]">
            <Link href={`/chat/${sessionId}`}>
              <Button variant="icon">
                <ArrowLeft className="w-[16px] h-[16px]" />
              </Button>
            </Link>
            <div>
              <div className="text-[18px] sm:text-[20px] font-display font-semibold">
                Extraction Dataset
              </div>
              <div className="text-[13px] text-text-dim flex items-center gap-[8px] min-w-0">
                <span className="truncate max-w-[42vw] sm:max-w-none">Session {sessionId}</span>
                <span className="w-[4px] h-[4px] bg-glass-border-strong rounded-full"></span>
                <span>Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-[10px] sm:gap-[16px] mb-[16px] sm:mb-[24px] shrink-0">
          <Card className="p-[12px] sm:p-[16px] flex items-center gap-[10px] sm:gap-[16px]">
            <div className="hidden sm:flex w-[40px] h-[40px] rounded-full bg-[rgba(130,170,255,0.08)] flex items-center justify-center text-text-mid">
              <Database className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[20px] sm:text-[24px] font-display font-semibold leading-none mb-[4px]">{totalRows}</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Total Rows</div>
            </div>
          </Card>
          
          <Card className="p-[12px] sm:p-[16px] flex items-center gap-[10px] sm:gap-[16px]">
            <div className="hidden sm:flex w-[40px] h-[40px] rounded-full bg-[rgba(52,211,153,0.1)] flex items-center justify-center text-success">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <div>
              <div className="text-[20px] sm:text-[24px] font-display font-semibold leading-none mb-[4px]">{avgConf}%</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Avg Confidence</div>
            </div>
          </Card>
          
          <Card className="p-[12px] sm:p-[16px] flex items-center gap-[10px] sm:gap-[16px]">
            <div className="hidden sm:flex w-[40px] h-[40px] rounded-full bg-[rgba(245,181,68,0.1)] flex items-center justify-center text-warn">
              <ShieldAlert className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[20px] sm:text-[24px] font-display font-semibold leading-none mb-[4px]">{flaggedCount}</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Flagged Fields</div>
            </div>
          </Card>
          
          <Card className="p-[12px] sm:p-[16px] flex items-center gap-[10px] sm:gap-[16px]">
            <div className="hidden sm:flex w-[40px] h-[40px] rounded-full bg-[rgba(79,216,255,0.1)] flex items-center justify-center text-cyan">
              <Columns3 className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[20px] sm:text-[24px] font-display font-semibold leading-none mb-[4px]">{totalCols}</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Columns</div>
            </div>
          </Card>
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col lg:flex-row gap-[16px] lg:gap-[24px] flex-1 lg:overflow-hidden lg:min-h-0">
          {/* Table Area */}
          <Card className="flex-1 min-w-0 p-[12px] sm:p-[16px] flex flex-col lg:overflow-hidden min-h-[360px]">
            <div className="flex flex-wrap items-center gap-[10px] sm:gap-[12px] mb-[16px] shrink-0">
              <Input 
                icon={<Search className="w-[15px] h-[15px]" />}
                placeholder="Search extracted data..."
                className="w-full sm:max-w-[320px]"
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
            
            {apiResponse?.truncated && (
              <p className="mb-[10px] text-[12px] text-warn shrink-0">Showing the first {rawData.length} of {apiResponse.total_rows} rows (storage limit).</p>
            )}
            <div className="flex-1 overflow-auto min-h-0">
              {rawData.length > 0 ? (
                <DataTable columns={columns} data={filteredData} />
              ) : (
                <div className="h-full flex items-center justify-center text-text-dim">
                  {isLoading ? "Loading session data..." : loadError ? loadError : "No data available. Run an extraction in the chat first."}
                </div>
              )}
            </div>
          </Card>
          
          {/* Export Panel */}
          <ExportPanel sessionId={sessionId !== "new" ? sessionId : undefined} />
        </div>
      </div>
    </div>
  );
}
