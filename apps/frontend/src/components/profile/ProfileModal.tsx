"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  X,
  User,
  Mail,
  ShieldCheck,
  ShieldAlert,
  Calendar,
  Key,
  Check,
  Loader2,
  Sparkles,
  ArrowRight,
  Copy,
  CheckCheck,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ApiClient } from "@/lib/api/client";
import type { SidebarUser } from "@/components/sidebar/Sidebar";

export interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: SidebarUser | null;
  onUserUpdated?: (updated: SidebarUser) => void;
}

export function ProfileModal({
  isOpen,
  onClose,
  user,
  onUserUpdated,
}: ProfileModalProps) {
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState(false);

  // Sync state if user changes
  React.useEffect(() => {
    if (user?.full_name) {
      setFullName(user.full_name);
    }
  }, [user?.full_name]);

  if (!isOpen) return null;

  const isGuest = Boolean(user?.is_guest);
  const email = user?.email || (isGuest ? "guest@webiscrap.session" : "No email linked");
  const initials = isGuest
    ? "G"
    : (user?.full_name?.trim() || user?.email || "U").slice(0, 2).toUpperCase();

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isGuest) return;
    setSaving(true);
    setError(null);
    setSavedSuccess(false);

    try {
      const updated = await ApiClient.updateMe({ full_name: fullName.trim() });
      setSavedSuccess(true);
      if (onUserUpdated && updated) {
        onUserUpdated(updated);
      }
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err: any) {
      setError(err?.message || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const copyUserId = () => {
    if (user?.id) {
      void navigator.clipboard.writeText(user.id);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="profile-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-[16px] bg-black/70 backdrop-blur-sm animate-in"
    >
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-hidden="true"
      />

      <Card
        variant="strong"
        className="relative z-10 w-full max-w-[500px] p-[24px] sm:p-[28px] bg-panel-strong border-glass-border-strong shadow-[0_24px_64px_rgba(0,0,0,0.6)] animate-[scaleIn_0.25s_cubic-bezier(0.16,1,0.3,1)_both]"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-[16px] border-b border-hair mb-[20px]">
          <div className="flex items-center gap-[10px]">
            <div className="w-[32px] h-[32px] rounded-[8px] bg-gradient-to-br from-signal-400 to-cyan flex items-center justify-center text-white shadow-[0_0_12px_rgba(20,119,245,0.35)]">
              <User className="w-[16px] h-[16px]" />
            </div>
            <div>
              <h2 id="profile-modal-title" className="text-[17px] font-display font-semibold text-text-hi leading-tight">
                Profile &amp; Details
              </h2>
              <p className="text-[12px] font-mono text-cyan">WEBISCRAP Identity</p>
            </div>
          </div>
          <Button
            variant="icon"
            onClick={onClose}
            aria-label="Close dialog"
            className="w-[30px] h-[30px] rounded-full hover:bg-white/10"
          >
            <X className="w-[16px] h-[16px]" />
          </Button>
        </div>

        {/* User Card Overview */}
        <div className="flex items-center gap-[16px] p-[16px] rounded-card bg-white/[0.02] border border-hair mb-[20px]">
          <div className="relative">
            <div className="w-[52px] h-[52px] rounded-full bg-gradient-to-br from-signal-400 via-signal-500 to-cyan-dim flex items-center justify-center font-mono text-[18px] font-bold text-white shadow-[0_0_16px_rgba(20,119,245,0.3)]">
              {initials}
            </div>
            <span
              className={`absolute bottom-0 right-0 w-[12px] h-[12px] rounded-full border-2 border-bg-0 ${
                isGuest ? "bg-warn" : "bg-success"
              }`}
              title={isGuest ? "Guest session" : "Active workspace"}
            />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-[8px] flex-wrap">
              <span className="font-display font-semibold text-[16px] text-text-hi truncate">
                {user?.full_name || (isGuest ? "Guest User" : "Workspace User")}
              </span>
              <span
                className={`font-mono text-[10px] uppercase tracking-wider px-[8px] py-[2px] rounded-pill border ${
                  isGuest
                    ? "border-warn/30 text-warn bg-warn/10"
                    : "border-success/30 text-success bg-success/10"
                }`}
              >
                {isGuest ? "Guest" : "Member"}
              </span>
            </div>
            <div className="text-[12.5px] text-text-dim truncate mt-[2px] font-mono flex items-center gap-[6px]">
              <Mail className="w-[12px] h-[12px] shrink-0 opacity-70" />
              <span className="truncate">{email}</span>
            </div>
          </div>
        </div>

        {/* Edit Full Name Form */}
        {!isGuest ? (
          <form onSubmit={handleSave} className="space-y-[14px] mb-[20px]">
            <div>
              <label htmlFor="full_name" className="block text-[12px] font-mono text-text-dim uppercase tracking-wider mb-[6px]">
                Full Name
              </label>
              <Input
                id="full_name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your display name"
                disabled={saving}
                className="text-[14px] py-[10px]"
              />
            </div>

            {error && (
              <div className="p-[10px] rounded-[8px] bg-red-500/10 border border-red-500/20 text-red-400 text-[12px]">
                {error}
              </div>
            )}

            <div className="flex items-center justify-between pt-[4px]">
              {savedSuccess ? (
                <span className="inline-flex items-center gap-[6px] text-[12.5px] text-success font-medium">
                  <Check className="w-[14px] h-[14px]" />
                  Saved successfully
                </span>
              ) : (
                <span className="text-[11.5px] text-text-dim">
                  Visible in workspace and export metadata
                </span>
              )}

              <Button
                type="submit"
                variant="primary"
                disabled={saving || fullName.trim() === (user?.full_name || "")}
                className="text-[13px] px-[16px] py-[8px]"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-[14px] h-[14px] animate-spin" />
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </Button>
            </div>
          </form>
        ) : (
          <div className="p-[14px] rounded-card bg-amber-500/[0.06] border border-amber-500/20 mb-[20px]">
            <div className="flex items-start gap-[10px]">
              <Sparkles className="w-[16px] h-[16px] text-warn shrink-0 mt-[2px]" />
              <div className="text-[12.5px] text-text-mid leading-[1.5]">
                You are currently browsing as a guest. Guest chats are ephemeral and cleared on logout.
                <div className="mt-[8px]">
                  <Link href="/signup" onClick={onClose} className="inline-flex items-center gap-[6px] text-cyan hover:text-signal-300 font-medium transition-colors">
                    Create a free account to save extractions
                    <ArrowRight className="w-[12px] h-[12px]" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Identity & Security Metadata */}
        <div className="border-t border-hair pt-[16px] space-y-[10px] text-[12px]">
          <div className="flex items-center justify-between py-[4px] text-text-mid">
            <span className="flex items-center gap-[6px] text-text-dim">
              <Key className="w-[13px] h-[13px] opacity-70" />
              Account ID
            </span>
            <button
              onClick={copyUserId}
              disabled={!user?.id}
              className="font-mono text-cyan hover:text-signal-300 flex items-center gap-[6px] cursor-pointer transition-colors"
              title="Copy User ID"
            >
              <span>{user?.id ? `${user.id.slice(0, 8)}...${user.id.slice(-6)}` : "Ephemeral"}</span>
              {copiedId ? (
                <CheckCheck className="w-[12px] h-[12px] text-success" />
              ) : (
                <Copy className="w-[12px] h-[12px] opacity-70" />
              )}
            </button>
          </div>

          <div className="flex items-center justify-between py-[4px] text-text-mid">
            <span className="flex items-center gap-[6px] text-text-dim">
              {user?.is_verified ? (
                <ShieldCheck className="w-[13px] h-[13px] text-success" />
              ) : (
                <ShieldAlert className="w-[13px] h-[13px] text-warn" />
              )}
              Email Verification
            </span>
            <span className={`font-mono text-[11px] ${user?.is_verified ? "text-success" : "text-warn"}`}>
              {user?.is_verified ? "Verified" : isGuest ? "N/A" : "Unverified"}
            </span>
          </div>

          <div className="flex items-center justify-between py-[4px] text-text-mid">
            <span className="flex items-center gap-[6px] text-text-dim">
              <Calendar className="w-[13px] h-[13px] opacity-70" />
              Session Security
            </span>
            <span className="font-mono text-[11px] text-text-mid">
              In-Memory Access Token + JTI
            </span>
          </div>
        </div>

        {/* Footer actions */}
        <div className="mt-[20px] pt-[14px] border-t border-hair flex items-center justify-end">
          <Button variant="ghost" onClick={onClose} className="text-[13px] py-[8px] px-[16px]">
            Done
          </Button>
        </div>
      </Card>
    </div>
  );
}
