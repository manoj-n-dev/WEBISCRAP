"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { useChatStore } from "@/lib/store/chat";
import { useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api/client";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    // FIX 7: Use silent refresh instead of localStorage check
    const init = async () => {
      const ok = await ApiClient.initAuth();
      if (!ok) {
        router.push("/login");
        return;
      }
      setAuthReady(true);
    };
    init();
  }, [router]);

  if (!authReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-0">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-signal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-[13px] text-text-dim font-mono">Authenticating...</span>
        </div>
      </div>
    );
  }

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

