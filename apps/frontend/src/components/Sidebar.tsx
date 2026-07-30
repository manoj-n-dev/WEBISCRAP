"use client";

import Image from "next/image";
import { Plus, MessageSquare, LogOut, PanelLeftClose } from "lucide-react";
import type { ChatSession } from "@/app/page";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onNewChat: () => void;
  sessions: ChatSession[];
}

export function Sidebar({ isOpen, onToggle, onNewChat, sessions }: SidebarProps) {
  if (!isOpen) return null;

  return (
    <aside className="w-64 h-full flex flex-col bg-sidebar border-r border-border shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Image
            src="/assets/inner-logo.png"
            alt="WEBISCRAP"
            width={28}
            height={28}
            className="rounded-md"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
            }}
          />
          <span className="text-sm font-semibold text-foreground tracking-tight">
            WEBISCRAP
          </span>
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-sidebar-hover transition-colors text-muted hover:text-foreground cursor-pointer"
          aria-label="Close sidebar"
        >
          <PanelLeftClose className="w-4 h-4" />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="px-3 py-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-border text-sm text-foreground hover:bg-sidebar-hover transition-colors cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-3">
        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-xs text-muted">No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            <p className="text-[11px] font-medium text-muted uppercase tracking-wider px-2 py-2">
              Recent
            </p>
            {sessions.map((session) => (
              <button
                key={session.id}
                className="w-full flex items-center gap-2 px-2 py-2 rounded-lg text-sm text-muted hover:text-foreground hover:bg-sidebar-hover transition-colors text-left cursor-pointer"
              >
                <MessageSquare className="w-4 h-4 shrink-0" />
                <span className="truncate">{session.title}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-3 border-t border-border">
        <button className="w-full flex items-center gap-2 px-2 py-2 rounded-lg text-sm text-muted hover:text-foreground hover:bg-sidebar-hover transition-colors cursor-pointer">
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
