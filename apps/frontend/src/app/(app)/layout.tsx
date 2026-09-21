"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Menu, ArrowLeft, Home } from "lucide-react";
import { Sidebar, type SidebarUser } from "@/components/sidebar/Sidebar";
import { Button } from "@/components/ui/Button";
import { useChatStore } from "@/lib/store/chat";
import { ApiClient } from "@/lib/api/client";
import { WarmUp } from "@/components/system/WarmUp";
import { useSlowHint } from "@/lib/useSlowHint";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authReady, setAuthReady] = useState(false);
  const [user, setUser] = useState<SidebarUser | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const sessions = useChatStore((s) => s.sessions);
  const slowAuth = useSlowHint(!authReady);

  useEffect(() => {
    const init = async () => {
      const ok = await ApiClient.initAuth();
      if (!ok) {
        useChatStore.getState().resetAll();
        router.replace("/login");
        return;
      }
      setAuthReady(true);          // render the app shell right away; profile + chat list load in parallel below
      const [me] = await Promise.allSettled([ApiClient.getMe(), useChatStore.getState().loadSessions()]);
      if (me.status === "fulfilled") {
        const u = me.value as SidebarUser & { id: string };
        setUser(u);
        useChatStore.getState().bindUser(String(u.id));   // a different identity than last time -> wipe stale chats
      }
    };
    void init();
  }, [router]);

  useEffect(() => setDrawerOpen(false), [pathname]);

  if (!authReady) {
    return (
      <div className="min-h-dvh flex items-center justify-center bg-bg-0 px-4">
        <WarmUp />
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-signal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-[13px] text-text-dim font-mono">{slowAuth ? "Waking the server…" : "Authenticating..."}</span>
          {slowAuth && <span className="text-[12px] text-text-dim max-w-[280px] text-center">The free server sleeps when idle; the first load can take up to a minute.</span>}
        </div>
      </div>
    );
  }

  const title = pathname.startsWith("/dataset")
    ? "Dataset"
    : sessions.find((s) => s.id === activeSessionId)?.title || "New extraction";

  return (
    <div className="relative h-dvh flex text-text-hi font-body overflow-hidden">
      <div className="bg-field"></div>

      {drawerOpen && <div className="fixed inset-0 z-30 bg-black/60 lg:hidden" onClick={() => setDrawerOpen(false)} aria-hidden />}
      <Sidebar user={user} open={drawerOpen} onNavigate={() => setDrawerOpen(false)} />

      <div className="flex-1 min-w-0 relative z-10 flex flex-col h-dvh overflow-hidden">
        <header className="h-[56px] sm:h-[60px] border-b border-hair flex items-center justify-between gap-[10px] px-[12px] sm:px-[20px] shrink-0 bg-[rgba(5,7,12,0.6)] backdrop-blur-md">
          <div className="flex items-center gap-[10px] min-w-0">
            <Button variant="icon" className="lg:hidden border-none" onClick={() => setDrawerOpen(true)} aria-label="Open menu">
              <Menu className="w-[20px] h-[20px]" />
            </Button>
            {pathname.startsWith("/dataset") ? (
              <button
                onClick={() => router.push(activeSessionId ? `/chat/${activeSessionId}` : "/chat/new")}
                className="flex items-center gap-1 text-[13px] text-text-dim hover:text-text-hi transition-colors cursor-pointer mr-1"
                title="Back to chat"
                aria-label="Back to chat"
              >
                <ArrowLeft className="w-[16px] h-[16px]" />
                <span className="hidden sm:inline">Back</span>
              </button>
            ) : null}
            <div className="flex items-center gap-[10px] text-[13.5px] min-w-0">
              <span className="text-text-mid truncate max-w-[50vw] sm:max-w-[400px]">{title}</span>
              <span className="hidden sm:block w-[4px] h-[4px] rounded-full bg-glass-border-strong"></span>
              <span className="hidden sm:block font-mono text-[11px] text-cyan uppercase tracking-[0.05em]">Active</span>
            </div>
          </div>
          <div className="flex items-center gap-[8px] shrink-0">
            <a
              href="/"
              title="Return to Home Page"
              aria-label="Return to Home Page"
              className="text-[12px] text-text-dim hover:text-text-hi px-2.5 py-1 rounded border border-white/5 hover:border-white/15 transition-all flex items-center gap-1.5"
            >
              <Home className="w-[14px] h-[14px]" />
              <span className="hidden sm:inline">Home</span>
            </a>
          </div>
        </header>
        <main className="flex-1 min-h-0 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
