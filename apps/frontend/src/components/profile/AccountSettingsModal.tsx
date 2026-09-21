"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  X,
  User,
  Settings,
  Mail,
  ShieldCheck,
  ShieldAlert,
  Loader2,
  Check,
  Copy,
  Sliders,
  MousePointer,
  Sparkles,
  Zap,
  RotateCcw,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ApiClient } from "@/lib/api/client";
import { useSound } from "@/lib/useSound";
import type { SidebarUser } from "@/components/sidebar/Sidebar";

export interface AccountSettingsModalProps {
  isOpen: boolean;
  initialTab?: "account" | "settings";
  onClose: () => void;
  user: SidebarUser | null;
  onUserUpdated?: (updated: SidebarUser) => void;
}

export function AccountSettingsModal({
  isOpen,
  initialTab = "account",
  onClose,
  user,
  onUserUpdated,
}: AccountSettingsModalProps) {
  const [activeTab, setActiveTab] = useState<"account" | "settings">(initialTab);
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState(false);

  const sound = useSound();

  // Settings states with localStorage persistence
  const [cursorEnabled, setCursorEnabled] = useState(true);
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // Sync initial tab and name on open
  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      if (user?.full_name) {
        setFullName(user.full_name);
      }
      // Load saved preferences
      try {
        const savedCursor = localStorage.getItem("webiscrap_cursor_enabled");
        if (savedCursor !== null) setCursorEnabled(savedCursor !== "false");
        const savedAnim = localStorage.getItem("webiscrap_animations_enabled");
        if (savedAnim !== null) setAnimationsEnabled(savedAnim !== "false");
        const savedSound = localStorage.getItem("webiscrap_sounds_enabled");
        if (savedSound !== null) setSoundEnabled(savedSound !== "false");
        else setSoundEnabled(true); // default ON
      } catch {
        // Safe fallback if local storage is restricted
      }
    }
  }, [isOpen, initialTab, user?.full_name]);

  // Play open sound when modal opens
  useEffect(() => {
    if (isOpen) sound.play("open");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  // Handle ESC key to close
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        sound.play("close");
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, sound]);

  if (!isOpen) return null;

  const isGuest = Boolean(user?.is_guest);
  const email = user?.email || (isGuest ? "guest@webiscrap.session" : "No email linked");
  const initials = isGuest
    ? "G"
    : (user?.full_name?.trim() || user?.email || "U").slice(0, 2).toUpperCase();

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isGuest) return;
    setSaving(true);
    setError(null);
    setSavedSuccess(false);

    try {
      const updated = await ApiClient.updateMe({ full_name: fullName.trim() });
      setSavedSuccess(true);
      sound.play("success");
      if (onUserUpdated && updated) {
        onUserUpdated(updated);
      }
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err: unknown) {
      sound.play("error");
      setError((err as { message?: string })?.message || "Failed to update profile");
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

  const toggleCursor = () => {
    const next = !cursorEnabled;
    setCursorEnabled(next);
    try {
      localStorage.setItem("webiscrap_cursor_enabled", String(next));
      window.dispatchEvent(new CustomEvent("webiscrap_cursor_toggle", { detail: { enabled: next } }));
      if (!next) {
        document.body.classList.add("no-custom-cursor");
      } else {
        document.body.classList.remove("no-custom-cursor");
      }
    } catch {
      // ignore
    }
  };

  const toggleAnimations = () => {
    const next = !animationsEnabled;
    setAnimationsEnabled(next);
    try {
      localStorage.setItem("webiscrap_animations_enabled", String(next));
    } catch {
      // ignore
    }
  };

  const toggleSound = () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    sound.setEnabled(next);
    if (next) {
      // Play immediately so the user hears what they just enabled
      setTimeout(() => sound.play("notify"), 50);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="account-settings-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center sm:p-[16px] bg-black/75 backdrop-blur-md animate-in"
    >
      <div className="fixed inset-0" onClick={() => { sound.play("close"); onClose(); }} aria-hidden="true" />

      <Card
        variant="strong"
        className="relative z-10 w-full sm:max-w-[520px] p-[20px] sm:p-[28px] bg-panel-strong border-glass-border-strong shadow-[0_24px_64px_rgba(0,0,0,0.7)] animate-[scaleIn_0.25s_cubic-bezier(0.16,1,0.3,1)_both] rounded-t-[20px] sm:rounded-[22px] max-h-[90dvh] overflow-y-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-[14px] border-b border-hair mb-[18px]">
          <div className="flex items-center gap-[10px]">
            <div className="w-[32px] h-[32px] rounded-[8px] bg-gradient-to-br from-signal-400 to-cyan flex items-center justify-center text-white shadow-[0_0_12px_rgba(20,119,245,0.35)]">
              {activeTab === "account" ? (
                <User className="w-[16px] h-[16px]" />
              ) : (
                <Settings className="w-[16px] h-[16px]" />
              )}
            </div>
            <div>
              <h2 id="account-settings-title" className="text-[17px] font-display font-semibold text-text-hi leading-tight">
                {activeTab === "account" ? "Account & Profile" : "Settings & Preferences"}
              </h2>
              <p className="text-[11.5px] font-mono text-cyan uppercase tracking-[0.06em]">WEBISCRAP Control Center</p>
            </div>
          </div>
          <Button
            variant="icon"
            onClick={() => { sound.play("close"); onClose(); }}
            className="border-none text-text-dim hover:text-text-hi"
            title="Close"
            aria-label="Close"
          >
            <X className="w-[16px] h-[16px]" />
          </Button>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-[6px] p-[3px] bg-black/40 border border-hair rounded-[8px] mb-[20px]">
          <button
            type="button"
            onClick={() => { sound.play("click"); setActiveTab("account"); }}
            className={`flex-1 flex items-center justify-center gap-[8px] py-[7px] text-[12.5px] font-medium rounded-[6px] transition-all cursor-pointer ${
              activeTab === "account"
                ? "bg-white/10 text-white shadow-[0_2px_8px_rgba(0,0,0,0.3)] border border-white/10"
                : "text-text-dim hover:text-text-mid hover:bg-white/5"
            }`}
          >
            <User className="w-[14px] h-[14px]" />
            Account &amp; Profile
          </button>
          <button
            type="button"
            onClick={() => { sound.play("click"); setActiveTab("settings"); }}
            className={`flex-1 flex items-center justify-center gap-[8px] py-[7px] text-[12.5px] font-medium rounded-[6px] transition-all cursor-pointer ${
              activeTab === "settings"
                ? "bg-white/10 text-white shadow-[0_2px_8px_rgba(0,0,0,0.3)] border border-white/10"
                : "text-text-dim hover:text-text-mid hover:bg-white/5"
            }`}
          >
            <Sliders className="w-[14px] h-[14px]" />
            Settings &amp; Preferences
          </button>
        </div>

        {/* TAB 1: ACCOUNT & PROFILE */}
        {activeTab === "account" && (
          <div className="space-y-[18px]">
            {/* User Identity Card */}
            <div className="flex items-center gap-[14px] p-[14px] rounded-[10px] bg-white/[0.03] border border-hair">
              <div className="w-[44px] h-[44px] rounded-full bg-gradient-to-br from-signal-400 to-cyan flex items-center justify-center font-mono text-[16px] font-bold text-white shadow-[0_0_12px_rgba(79,216,255,0.4)] shrink-0">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-[8px]">
                  <span className="text-[14px] font-medium text-text-hi truncate">
                    {user?.full_name || (isGuest ? "Guest User" : "WEBISCRAP Operator")}
                  </span>
                  <span className="text-[10px] font-mono uppercase tracking-[0.08em] px-[7px] py-[2px] rounded-full bg-cyan/15 text-cyan border border-cyan/30">
                    {isGuest ? "Guest" : "Pro Plan"}
                  </span>
                </div>
                <div className="text-[12px] text-text-dim truncate mt-[2px]">{email}</div>
              </div>
            </div>

            {/* Guest Conversion Alert */}
            {isGuest && (
              <div className="p-[12px] rounded-[8px] bg-signal-400/10 border border-signal-400/30 flex items-start gap-[10px]">
                <ShieldAlert className="w-[16px] h-[16px] text-signal-300 shrink-0 mt-[2px]" />
                <div className="text-[12px] text-text-mid">
                  <span className="font-semibold text-text-hi">You are currently in guest mode. </span>
                  Your extraction sessions will be lost if browser cookies are cleared.{" "}
                  <Link
                    href="/signup"
                    onClick={onClose}
                    className="text-cyan underline hover:text-white font-medium"
                  >
                    Create a free permanent account
                  </Link>{" "}
                  to keep all data.
                </div>
              </div>
            )}

            {/* Profile Form */}
            {!isGuest && (
              <form onSubmit={handleSaveProfile} className="space-y-[12px]">
                <div>
                  <label className="block text-[12px] font-mono text-text-dim uppercase tracking-[0.06em] mb-[6px]">
                    Display Name
                  </label>
                  <Input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter your name"
                    disabled={saving}
                    className="w-full text-[13.5px]"
                  />
                </div>

                {error && (
                  <div className="p-[10px] rounded-[6px] bg-red-500/10 border border-red-500/20 text-red-400 text-[12px]">
                    {error}
                  </div>
                )}

                <div className="flex items-center justify-between pt-[4px]">
                  <span className="text-[11.5px] text-text-dim">
                    {savedSuccess ? (
                      <span className="text-emerald-400 flex items-center gap-[4px]">
                        <Check className="w-[13px] h-[13px]" /> Profile updated successfully
                      </span>
                    ) : (
                      "Changes reflect instantly in your session."
                    )}
                  </span>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={saving || fullName.trim() === (user?.full_name || "")}
                    className="text-[12.5px] px-[16px] py-[6px]"
                  >
                    {saving ? (
                      <>
                        <Loader2 className="w-[13px] h-[13px] animate-spin mr-[6px]" /> Saving...
                      </>
                    ) : (
                      "Save Profile"
                    )}
                  </Button>
                </div>
              </form>
            )}

            {/* Metadata Rows */}
            <div className="pt-[8px] border-t border-hair space-y-[8px]">
              <div className="flex items-center justify-between py-[6px] text-[12.5px]">
                <div className="flex items-center gap-[8px] text-text-dim">
                  <Mail className="w-[14px] h-[14px]" />
                  <span>Email Verification</span>
                </div>
                <div className="flex items-center gap-[6px]">
                  {!isGuest ? (
                    <span className="flex items-center gap-[4px] text-emerald-400 text-[12px] font-medium">
                      <ShieldCheck className="w-[13px] h-[13px]" /> Verified
                    </span>
                  ) : (
                    <span className="text-text-dim text-[12px]">Ephemeral</span>
                  )}
                </div>
              </div>

              {user?.id && (
                <div className="flex items-center justify-between py-[6px] text-[12.5px]">
                  <div className="flex items-center gap-[8px] text-text-dim">
                    <Zap className="w-[14px] h-[14px]" />
                    <span>Account UUID</span>
                  </div>
                  <button
                    type="button"
                    onClick={copyUserId}
                    className="flex items-center gap-[6px] text-text-mid hover:text-cyan font-mono text-[11px] p-[4px] -mr-[4px] rounded hover:bg-white/5 transition-colors cursor-pointer"
                    title="Copy Account ID"
                  >
                    <span className="max-w-[140px] truncate">{user.id}</span>
                    {copiedId ? (
                      <Check className="w-[12px] h-[12px] text-emerald-400" />
                    ) : (
                      <Copy className="w-[12px] h-[12px]" />
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: SETTINGS & PREFERENCES */}
        {activeTab === "settings" && (
          <div className="space-y-[16px]">
            {/* Setting 1: Custom HUD Cursor */}
            <div className="flex items-center justify-between p-[12px] rounded-[10px] bg-white/[0.03] border border-hair">
              <div className="flex items-start gap-[10px] pr-[12px]">
                <div className="w-[32px] h-[32px] rounded-[6px] bg-cyan/10 border border-cyan/20 flex items-center justify-center text-cyan shrink-0 mt-[2px]">
                  <MousePointer className="w-[15px] h-[15px]" />
                </div>
                <div>
                  <div className="text-[13px] font-medium text-text-hi">Futuristic HUD Cursor</div>
                  <div className="text-[11.5px] text-text-dim leading-snug">
                    Floating reticle cursor with magnetic hover states (desktop only).
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={toggleCursor}
                className={`w-[40px] h-[22px] rounded-full p-[2px] transition-colors cursor-pointer shrink-0 ${
                  cursorEnabled ? "bg-cyan" : "bg-white/15"
                }`}
                aria-label="Toggle custom cursor"
              >
                <div
                  className={`w-[18px] h-[18px] rounded-full bg-white transition-transform ${
                    cursorEnabled ? "translate-x-[18px]" : "translate-x-0"
                  }`}
                />
              </button>
            </div>

            {/* Setting 2: Micro-Animations */}
            <div className="flex items-center justify-between p-[12px] rounded-[10px] bg-white/[0.03] border border-hair">
              <div className="flex items-start gap-[10px] pr-[12px]">
                <div className="w-[32px] h-[32px] rounded-[6px] bg-signal-400/10 border border-signal-400/20 flex items-center justify-center text-signal-400 shrink-0 mt-[2px]">
                  <Sparkles className="w-[15px] h-[15px]" />
                </div>
                <div>
                  <div className="text-[13px] font-medium text-text-hi">Fluid Micro-Animations</div>
                  <div className="text-[11.5px] text-text-dim leading-snug">
                    Enable smooth entrance slides, card glows, and message reveals.
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={toggleAnimations}
                className={`w-[40px] h-[22px] rounded-full p-[2px] transition-colors cursor-pointer shrink-0 ${
                  animationsEnabled ? "bg-cyan" : "bg-white/15"
                }`}
                aria-label="Toggle micro-animations"
              >
                <div
                  className={`w-[18px] h-[18px] rounded-full bg-white transition-transform ${
                    animationsEnabled ? "translate-x-[18px]" : "translate-x-0"
                  }`}
                />
              </button>
            </div>

            {/* Setting 3: Interface Audio Feedback */}
            <div className="flex items-center justify-between p-[12px] rounded-[10px] bg-white/[0.03] border border-hair">
              <div className="flex items-start gap-[10px] pr-[12px]">
                <div className="w-[32px] h-[32px] rounded-[6px] bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0 mt-[2px]">
                  {soundEnabled ? (
                    <Volume2 className="w-[15px] h-[15px]" />
                  ) : (
                    <VolumeX className="w-[15px] h-[15px]" />
                  )}
                </div>
                <div>
                  <div className="text-[13px] font-medium text-text-hi">Interface Sound Cues</div>
                  <div className="text-[11.5px] text-text-dim leading-snug">
                    Subtle synthetic audio feedback on scraping completion.
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={toggleSound}
                className={`w-[40px] h-[22px] rounded-full p-[2px] transition-colors cursor-pointer shrink-0 ${
                  soundEnabled ? "bg-cyan" : "bg-white/15"
                }`}
                aria-label="Toggle interface audio"
              >
                <div
                  className={`w-[18px] h-[18px] rounded-full bg-white transition-transform ${
                    soundEnabled ? "translate-x-[18px]" : "translate-x-0"
                  }`}
                />
              </button>
            </div>

            {/* Engine Metadata Footer */}
            <div className="pt-[10px] border-t border-hair flex items-center justify-between text-[11.5px] text-text-dim">
              <span>WEBISCRAP Core Engine</span>
              <span className="font-mono text-cyan">v1.2.0-prod</span>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
