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
  const [user, setUser] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  
  useEffect(() => {
    const fetchSessionsAndUser = async () => {
      try {
        const [sessionsRes, userRes] = await Promise.allSettled([
          ApiClient.getSessions(),
          ApiClient.getMe()
        ]);
        if (sessionsRes.status === "fulfilled" && sessionsRes.value?.sessions) {
          const now = Date.now() / 1000;
          const oneDay = 86400;
          const mapped = sessionsRes.value.sessions.map((s: string | any, i: number) => {
            const id = typeof s === 'string' ? s : s.id;
            const title = typeof s === 'string' ? `Extraction ${i+1}` : (s.title || `Extraction ${i+1}`);
            const timestamp = typeof s === 'object' && s.timestamp ? s.timestamp : null;
            let date: "today" | "yesterday" | "older" = "today";
            if (timestamp) {
              const diff = now - timestamp;
              date = diff < oneDay ? "today" : (diff < oneDay * 2 ? "yesterday" : "older");
            }
            return { id, title, date };
          });
          setSessions(mapped);
        }
        if (userRes.status === "fulfilled" && userRes.value) {
          setUser(userRes.value);
        }
      } catch (err) {
        console.error("Failed to load sidebar data:", err);
      }
    };
    fetchSessionsAndUser();
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

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const todaySessions = filteredSessions.filter(s => s.date === "today");
  const yesterdaySessions = filteredSessions.filter(s => s.date === "yesterday");
  const olderSessions = filteredSessions.filter(s => s.date === "older");

  // FIX 11 (M2): Real user info derivation
  const displayName = user?.full_name || (user?.email ? user.email.split("@")[0] : (user?.is_guest ? "Guest" : "User"));
  const initials = user?.full_name
    ? user.full_name.trim().split(/\s+/).map((n: string) => n[0]).join("").slice(0, 2).toUpperCase()
    : (user?.email ? user.email.slice(0, 2).toUpperCase() : (user?.is_guest ? "GU" : "US"));
  const workspaceText = user?.is_guest ? "Guest session" : "Personal workspace";

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
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
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

        {olderSessions.length > 0 && (
          <>
            <div className="m-[20px_6px_8px] font-mono text-[10.5px] tracking-[0.14em] text-text-dim uppercase">
              Older
            </div>
            {olderSessions.map(session => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={activeSessionId === session.id}
                onClick={() => handleSelectSession(session.id)}
              />
            ))}
          </>
        )}

        {searchQuery && filteredSessions.length === 0 && (
          <div className="p-[20px_10px] text-center text-[12px] text-text-dim">
            No matching sessions
          </div>
        )}
      </div>

      <div className="mt-auto pt-[14px] border-t border-hair flex items-center justify-between pl-[6px]">
        <div className="flex items-center gap-[10px] min-w-0">
          <div className="w-[28px] h-[28px] rounded-full bg-gradient-to-br from-signal-400 to-cyan-dim flex items-center justify-center font-mono text-[11px] text-white shrink-0">
            {initials}
          </div>
          <div className="min-w-0">
            <div className="text-[12.5px] text-text-hi truncate">{displayName}</div>
            <div className="text-[11px] text-text-dim truncate">{workspaceText}</div>
          </div>
        </div>
        
        <Button variant="icon" className="border-none hover:text-red-400 shrink-0" onClick={handleLogout} title="Log out">
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
