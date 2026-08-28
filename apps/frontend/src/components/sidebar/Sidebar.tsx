import React, { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Plus, Search, MessageSquare, LogOut } from "lucide-react";

import { useChatStore } from "@/lib/store/chat";
import { useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api/client";

export interface Session {
  id: string;
  title: string;
  date: "today" | "yesterday" | "older";
}

export function Sidebar() {
  const router = useRouter();
  const { activeSessionId, setActiveSession } = useChatStore();
  const [sessions, setSessions] = useState<Session[]>([]);
  
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const result = await ApiClient.getSessions();
        // The backend returns a list of session IDs/metadata. Map it to the Session format.
        // For MVP, if backend returns just strings, we mock the title/date.
        if (result && result.sessions) {
          const mapped = result.sessions.map((s: string | any, i: number) => ({
            id: typeof s === 'string' ? s : s.id,
            title: typeof s === 'string' ? `Extraction ${i+1}` : s.title || `Extraction ${i+1}`,
            date: "today" // simplified for MVP
          }));
          setSessions(mapped);
        }
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    };
    fetchSessions();
  }, []);
  
  const handleNewSession = () => {
    setActiveSession("new");
    router.push("/chat/new");
  };

  const handleSelectSession = (id: string) => {
    setActiveSession(id);
    router.push(`/chat/${id}`);
  };

  const handleLogout = async () => {
    await ApiClient.logout();
    router.push("/login");
  };

  const todaySessions = sessions.filter(s => s.date === "today");
  const yesterdaySessions = sessions.filter(s => s.date === "yesterday");

  return (
    <aside className="w-[264px] border-r border-hair flex flex-col p-[16px_14px] bg-bg-0 z-20 shrink-0 h-screen overflow-y-auto">
      <div className="flex items-center gap-[9px] p-[6px_6px_18px]">
        <Logo variant="lockup" size={22} />
      </div>

      <button
        onClick={handleNewSession}
        className="flex items-center gap-[8px] p-[10px_12px] rounded-sm border border-glass-border-strong text-[13.5px] text-text-hi cursor-pointer bg-[rgba(20,119,245,0.06)] hover:bg-[rgba(20,119,245,0.12)] transition-colors"
      >
        <Plus className="w-[18px] h-[18px]" />
        New extraction
      </button>

      <div className="mt-[14px]">
        <Input 
          icon={<Search className="w-[15px] h-[15px]" />} 
          placeholder="Search sessions" 
          className="text-[13px] py-[10px]"
        />
      </div>

      <div className="flex-1 mt-[8px] overflow-y-auto">
        {todaySessions.length > 0 && (
          <>
            <div className="m-[20px_6px_8px] font-mono text-[10.5px] tracking-[0.14em] text-text-dim uppercase">
              Today
            </div>
            {todaySessions.map(session => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={activeSessionId === session.id}
                onClick={() => handleSelectSession(session.id)}
              />
            ))}
          </>
        )}

        {yesterdaySessions.length > 0 && (
          <>
            <div className="m-[20px_6px_8px] font-mono text-[10.5px] tracking-[0.14em] text-text-dim uppercase">
              Yesterday
            </div>
            {yesterdaySessions.map(session => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={activeSessionId === session.id}
                onClick={() => handleSelectSession(session.id)}
              />
            ))}
          </>
        )}
      </div>

      <div className="mt-auto pt-[14px] border-t border-hair flex items-center justify-between pl-[6px]">
        <div className="flex items-center gap-[10px]">
          <div className="w-[28px] h-[28px] rounded-full bg-gradient-to-br from-signal-400 to-cyan-dim flex items-center justify-center font-mono text-[11px] text-white">
            MN
          </div>
          <div>
            <div className="text-[12.5px] text-text-hi">Manoj</div>
            <div className="text-[11px] text-text-dim">Free workspace</div>
          </div>
        </div>
        
        <Button variant="icon" className="border-none hover:text-red-400" onClick={handleLogout}>
          <LogOut className="w-[15px] h-[15px]" />
        </Button>
      </div>
    </aside>
  );
}

function SessionItem({ session, isActive, onClick }: { session: Session; isActive: boolean; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "p-[9px_10px] rounded-[8px] text-[13px] cursor-pointer flex items-center gap-[8px] transition-colors",
        isActive
          ? "bg-[rgba(20,119,245,0.1)] text-text-hi border border-glass-border"
          : "text-text-mid hover:bg-[rgba(255,255,255,0.035)] border border-transparent"
      )}
    >
      <MessageSquare className="w-[14px] h-[14px] shrink-0 text-text-dim" />
      <span className="truncate">{session.title}</span>
    </div>
  );
}
