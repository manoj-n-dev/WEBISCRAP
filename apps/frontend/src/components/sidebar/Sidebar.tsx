"use client";

import React, { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Plus, Search, MessageSquare, LogOut, Trash2, Pencil, Check, X, Settings } from "lucide-react";
import { useChatStore, type SessionSummary } from "@/lib/store/chat";
import { ApiClient } from "@/lib/api/client";

export interface SidebarUser {
  id?: string;
  email?: string | null;
  full_name?: string | null;
  is_guest?: boolean;
  is_verified?: boolean;
  created_at?: string;
}

export interface SidebarProps {
  user: SidebarUser | null;
  open: boolean;                 // mobile drawer state (ignored on lg+)
  onNavigate: () => void;
  onUserUpdated?: (updated: SidebarUser) => void;
  onOpenAccount?: () => void;
  onOpenSettings?: () => void;
}

const DAY = 86400;

export function Sidebar({ user, open, onNavigate, onUserUpdated, onOpenAccount, onOpenSettings }: SidebarProps) {
  const router = useRouter();
  const { sessions, sessionsLoaded, activeSessionId, startNewChat, removeSession, renameSession } = useChatStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [currentUser, setCurrentUser] = useState<SidebarUser | null>(user);

  React.useEffect(() => {
    setCurrentUser(user);
  }, [user]);

  const groups = useMemo(() => {
    const now = Date.now() / 1000;
    const q = searchQuery.toLowerCase();
    const list = sessions.filter((s) => s.title.toLowerCase().includes(q));
    return {
      total: list.length,
      Today: list.filter((s) => now - s.timestamp < DAY),
      Yesterday: list.filter((s) => now - s.timestamp >= DAY && now - s.timestamp < DAY * 2),
      Older: list.filter((s) => now - s.timestamp >= DAY * 2),
    };
  }, [sessions, searchQuery]);

  const handleNew = () => {
    startNewChat();
    router.push("/chat/new");
    onNavigate();
  };
  const handleSelect = (id: string) => {
    router.push(`/chat/${id}`);
    onNavigate();
  };
  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this chat and its data?")) return;
    const wasActive = activeSessionId === id;
    try {
      await removeSession(id);
      if (wasActive) router.push("/chat/new");
    } catch {
      window.alert("Could not delete this chat. Please try again.");
    }
  };
  const handleRename = async (id: string, newTitle: string) => {
    try {
      await renameSession(id, newTitle);
    } catch {
      window.alert("Could not rename this chat. Please try again.");
    }
  };
  const handleLogout = async () => {
    await ApiClient.logout();
    useChatStore.getState().resetAll();       // nothing from this identity may survive in memory
    router.replace("/login");
  };

  const activeUser = currentUser || user;
  const displayName = activeUser?.full_name || (activeUser?.email ? activeUser.email.split("@")[0] : activeUser?.is_guest ? "Guest" : "User");
  const initials = activeUser?.full_name
    ? activeUser.full_name.trim().split(/\s+/).map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : activeUser?.email ? activeUser.email.slice(0, 2).toUpperCase() : activeUser?.is_guest ? "GU" : "US";

  return (
    <aside
      className={cn(
        "border-r border-hair flex flex-col p-[16px_14px] bg-bg-0 z-40 shrink-0 h-dvh overflow-y-auto",
        "fixed inset-y-0 left-0 w-[290px] max-w-[85vw] transition-transform duration-200 lg:static lg:w-[264px] lg:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full",
      )}
    >
      <div className="flex items-center gap-[9px] p-[6px_6px_18px]">
        <Logo variant="lockup" size={22} />
      </div>

      <button
        onClick={handleNew}
        className="flex items-center gap-[8px] p-[10px_12px] rounded-sm border border-glass-border-strong text-[13.5px] text-text-hi cursor-pointer bg-[rgba(20,119,245,0.06)] hover:bg-[rgba(20,119,245,0.12)] transition-colors"
      >
        <Plus className="w-[18px] h-[18px]" />
        New extraction
      </button>

      <div className="mt-[14px]">
        <Input icon={<Search className="w-[15px] h-[15px]" />} placeholder="Search chats" className="text-[13px] py-[10px]" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
      </div>

      <div className="flex-1 mt-[8px] overflow-y-auto">
        {(["Today", "Yesterday", "Older"] as const).map((label) =>
          groups[label].length > 0 ? (
            <div key={label}>
              <div className="m-[20px_6px_8px] font-mono text-[10.5px] tracking-[0.14em] text-text-dim uppercase">{label}</div>
              {groups[label].map((s) => (
                <SessionItem
                  key={s.id}
                  session={s}
                  isActive={activeSessionId === s.id}
                  onClick={() => handleSelect(s.id)}
                  onDelete={() => handleDelete(s.id)}
                  onRename={(newTitle) => handleRename(s.id, newTitle)}
                />
              ))}
            </div>
          ) : null,
        )}
        {sessionsLoaded && groups.total === 0 && (
          <div className="p-[20px_10px] text-center text-[12px] text-text-dim">{searchQuery ? "No matching chats" : "No chats yet — start your first extraction."}</div>
        )}
      </div>

      <div className="mt-auto pt-[14px] border-t border-hair flex items-center justify-between gap-[6px] pl-[6px]">
        <button
          onClick={onOpenAccount}
          className="flex items-center gap-[10px] min-w-0 flex-1 text-left p-[4px] -ml-[4px] rounded-sm hover:bg-white/5 transition-colors cursor-pointer group"
          title="View profile & account details"
          aria-label="View profile & account details"
        >
          <div className="w-[28px] h-[28px] rounded-full bg-gradient-to-br from-signal-400 to-cyan-dim flex items-center justify-center font-mono text-[11px] text-white shrink-0 group-hover:shadow-[0_0_8px_rgba(79,216,255,0.4)] transition-all">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-[12.5px] text-text-hi truncate group-hover:text-cyan transition-colors">{displayName}</div>
            <div className="text-[11px] text-text-dim truncate">{activeUser?.is_guest ? "Guest session" : "Account & Settings"}</div>
          </div>
        </button>

        <div className="flex items-center gap-[2px] shrink-0">
          <Button
            variant="icon"
            className="border-none hover:text-cyan"
            onClick={onOpenSettings}
            title="Account settings & preferences"
            aria-label="Account settings & preferences"
          >
            <Settings className="w-[14px] h-[14px]" />
          </Button>
          <Button
            variant="icon"
            className="border-none hover:text-red-400"
            onClick={handleLogout}
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="w-[14px] h-[14px]" />
          </Button>
        </div>
      </div>
    </aside>
  );
}

function SessionItem({
  session,
  isActive,
  onClick,
  onDelete,
  onRename,
}: {
  session: SessionSummary;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
  onRename: (newTitle: string) => Promise<void>;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(session.title);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    const trimmed = editTitle.trim();
    if (!trimmed || trimmed === session.title) {
      setIsEditing(false);
      setEditTitle(session.title);
      return;
    }
    setSaving(true);
    try {
      await onRename(trimmed);
      setIsEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      void handleSave();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setIsEditing(false);
      setEditTitle(session.title);
    }
  };

  if (isEditing) {
    return (
      <div
        className={cn(
          "p-[6px_8px] rounded-[8px] text-[13px] flex items-center gap-[6px] border bg-[rgba(20,119,245,0.08)] border-signal-400/40 my-[2px]",
        )}
      >
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
          disabled={saving}
          maxLength={80}
          className="flex-1 min-w-0 bg-transparent text-text-hi text-[12.5px] border-b border-signal-400 focus:outline-none px-1 py-0.5"
        />
        <button
          onClick={handleSave}
          disabled={saving}
          aria-label="Save title"
          title="Save title (Enter)"
          className="shrink-0 w-[22px] h-[22px] rounded flex items-center justify-center text-cyan hover:bg-white/10 cursor-pointer"
        >
          <Check className="w-[13px] h-[13px]" />
        </button>
        <button
          onClick={() => {
            setIsEditing(false);
            setEditTitle(session.title);
          }}
          disabled={saving}
          aria-label="Cancel rename"
          title="Cancel (Esc)"
          className="shrink-0 w-[22px] h-[22px] rounded flex items-center justify-center text-text-dim hover:text-text-hi hover:bg-white/10 cursor-pointer"
        >
          <X className="w-[13px] h-[13px]" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "group p-[9px_10px] rounded-[8px] text-[13px] flex items-center gap-[8px] transition-colors border",
        isActive ? "bg-[rgba(20,119,245,0.1)] text-text-hi border-glass-border" : "text-text-mid hover:bg-[rgba(255,255,255,0.035)] border-transparent",
      )}
    >
      <button onClick={onClick} className="flex items-center gap-[8px] flex-1 min-w-0 text-left cursor-pointer">
        <MessageSquare className="w-[14px] h-[14px] shrink-0 text-text-dim" />
        <span className="truncate">{session.title}</span>
      </button>
      <div className="flex items-center gap-[2px] shrink-0 lg:opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setEditTitle(session.title);
            setIsEditing(true);
          }}
          aria-label="Rename chat"
          title="Rename chat"
          className="w-[24px] h-[24px] rounded-md flex items-center justify-center text-text-dim hover:text-text-hi hover:bg-white/5 cursor-pointer"
        >
          <Pencil className="w-[12px] h-[12px]" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          aria-label="Delete chat"
          title="Delete chat"
          className="w-[24px] h-[24px] rounded-md flex items-center justify-center text-text-dim hover:text-red-400 hover:bg-white/5 cursor-pointer"
        >
          <Trash2 className="w-[13px] h-[13px]" />
        </button>
      </div>
    </div>
  );
}
