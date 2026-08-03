"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, Search, Filter, Database, Clock, ShieldAlert } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ConfidenceBar } from "@/components/dataset/ConfidenceBar";
import { DataTable } from "@/components/dataset/DataTable";
import { ExportPanel } from "@/components/dataset/ExportPanel";
import { ColumnDef } from "@tanstack/react-table";

// Dummy data mirroring the reference HTML
const mockData = [
  { id: "1", title: "ASUS Vivobook 15", price: "₹52,990", rating: "4.2", processor: "Core i5", conf: 0.98 },
  { id: "2", title: "HP Pavilion 14", price: "₹58,500", rating: "4.4", processor: "Ryzen 5", conf: 0.94 },
  { id: "3", title: "Acer Swift 3", price: "₹54,999", rating: "4.3", processor: "Core i5", conf: 0.88 },
  { id: "4", title: "Lenovo IdeaPad Slim 3", price: "₹51,490", rating: "4.1", processor: "Ryzen 5", conf: 0.72 },
  { id: "5", title: "Dell Inspiron 3511", price: "₹55,200", rating: "4.0", processor: "Core i5", conf: 0.65 },
];

const columns: ColumnDef<typeof mockData[0]>[] = [
  { accessorKey: "title", header: "TITLE" },
  { accessorKey: "price", header: "PRICE" },
  { accessorKey: "rating", header: "RATING" },
  { accessorKey: "processor", header: "PROCESSOR" },
  { 
    accessorKey: "conf", 
    header: "CONFIDENCE",
    cell: ({ row }) => <ConfidenceBar score={row.original.conf} />
  },
];

export default function DatasetPage() {
  return (
    <div className="flex flex-col h-full bg-bg-0 text-text-hi font-body overflow-hidden">
      <div className="bg-field"></div>
      
      <div className="relative z-10 flex flex-col h-full overflow-hidden p-[24px]">
        {/* Top Header */}
        <div className="flex items-center justify-between mb-[24px] shrink-0">
          <div className="flex items-center gap-[16px]">
            <Link href="/chat/1">
              <Button variant="icon">
                <ArrowLeft className="w-[16px] h-[16px]" />
              </Button>
            </Link>
            <div>
              <div className="text-[20px] font-display font-semibold">Flipkart laptops over 50k</div>
              <div className="text-[13px] text-text-dim flex items-center gap-[8px]">
                <span>Extracted today at 2:45 PM</span>
                <span className="w-[4px] h-[4px] bg-glass-border-strong rounded-full"></span>
                <span>Source: flipkart.com</span>
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
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">42</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Total Rows</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(52,211,153,0.1)] flex items-center justify-center text-success">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">94%</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Avg Confidence</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(245,181,68,0.1)] flex items-center justify-center text-warn">
              <ShieldAlert className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">3</div>
              <div className="text-[12px] text-text-dim uppercase tracking-[0.05em] font-mono">Flagged Fields</div>
            </div>
          </Card>
          
          <Card className="p-[16px] flex items-center gap-[16px]">
            <div className="w-[40px] h-[40px] rounded-full bg-[rgba(79,216,255,0.1)] flex items-center justify-center text-cyan">
              <Clock className="w-[20px] h-[20px]" />
            </div>
            <div>
              <div className="text-[24px] font-display font-semibold leading-none mb-[4px]">4.2s</div>
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
              <DataTable columns={columns} data={mockData} />
            </div>
          </Card>
          
          {/* Export Panel */}
          <ExportPanel 
            onExport={(fmt) => console.log(`Exporting as ${fmt}`)} 
            className="w-[280px] shrink-0" 
          />
        </div>
      </div>
    </div>
  );
}
