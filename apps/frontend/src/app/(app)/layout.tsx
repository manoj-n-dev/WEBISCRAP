"use client";

import React from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { useChatStore } from "@/lib/store/chat";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen flex text-text-hi font-body overflow-hidden">
      <div className="bg-field"></div>
      
      {/* Sidebar - fixed width */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex-1 relative z-10 flex flex-col h-screen overflow-hidden">
        {/* Topbar */}
        <header className="h-[60px] border-b border-hair flex items-center justify-between px-[20px] shrink-0 bg-[rgba(5,7,12,0.6)] backdrop-blur-md">
          <div className="flex items-center gap-[10px] text-[13.5px]">
            <span className="text-text-mid truncate max-w-[300px]">New extraction</span>
            <span className="w-[4px] h-[4px] rounded-full bg-glass-border-strong"></span>
            <span className="font-mono text-[11px] text-cyan uppercase tracking-[0.05em]">Active</span>
          </div>
        </header>
        
        {/* Scrollable content area */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
