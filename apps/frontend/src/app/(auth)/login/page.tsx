"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { Mail, Lock, UserRound, ArrowRight } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { cn } from "@/lib/utils";
import { SocialAuth } from "@/components/auth/SocialAuth";
import { useChatStore } from "@/lib/store/chat";
import { useSlowHint } from "@/lib/useSlowHint";
import { useSound } from "@/lib/useSound";

export default function LoginPage() {
  const router = useRouter();
  const sound = useSound();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [staySignedIn, setStaySignedIn] = React.useState(true);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const [isUnverified, setIsUnverified] = React.useState(false);
  const slow = useSlowHint(loading);
  const [resending, setResending] = React.useState(false);
  const [resendNotice, setResendNotice] = React.useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setIsUnverified(false);
    setResendNotice(null);
    try {
      const response = await ApiClient.login(email, password, staySignedIn);
      if (response.access_token) {
        sound.play("login");
        useChatStore.getState().resetAll();     // never show a previous account's chats
        ApiClient.setToken(response.access_token);
        router.push("/chat/new");
      }
    } catch (err: any) {
      sound.play("error");
      const msg = err.message || "Failed to sign in";
      setError(msg);
      if (err.status === 403 || msg.toLowerCase().includes("not verified")) {
        setIsUnverified(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!email) return;
    setResending(true);
    setResendNotice(null);
    try {
      const res: any = await ApiClient.resendVerification(email);
      setResendNotice(res.message || "Verification email sent. Check your inbox.");
    } catch (err: any) {
      setResendNotice(err.message || "Failed to resend. Please try again later.");
    } finally {
      setResending(false);
    }
  };

  const handleGuestLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await ApiClient.guestLogin();
      if (response.access_token) {
        sound.play("login");
        useChatStore.getState().resetAll();
        ApiClient.setToken(response.access_token);
        router.push("/chat/new");
      }
    } catch (err: any) {
      sound.play("error");
      setError(err.message || "Failed to start guest session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card variant="strong" className="p-[22px] sm:p-[32px] animate-in">
        <div className="text-center mb-[28px]">
          <h1 className="text-[24px] font-display font-semibold mb-[8px]">Welcome Back</h1>
          <p className="text-[14px] text-text-dim">Sign in to access your extractions</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-[16px]">
          <Input 
            type="email" 
            placeholder="Email address" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            icon={<Mail className="w-[16px] h-[16px]" />} 
            required 
            disabled={loading}
          />
          
          <Input 
            type="password" 
            placeholder="Password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            icon={<Lock className="w-[16px] h-[16px]" />} 
            required 
            disabled={loading}
          />
          
          <div className="flex items-center justify-between mt-[4px]">
            <label 
              className="flex items-center gap-[8px] cursor-pointer group select-none"
              onClick={() => setStaySignedIn(!staySignedIn)}
            >
              <div className={cn(
                "w-[16px] h-[16px] rounded-[4px] border transition-colors flex items-center justify-center",
                staySignedIn
                  ? "bg-signal-400 border-signal-400 text-bg-0"
                  : "border-glass-border-strong group-hover:border-signal-300 text-transparent"
              )}>
                <svg className="w-[10px] h-[10px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <span className="text-[13px] text-text-mid group-hover:text-text-hi transition-colors">Stay signed in</span>
            </label>
            <a href="/forgot-password" className="text-sm font-medium text-text-hi hover:text-white transition-colors">
              Forgot password?
            </a>
          </div>
          
          <Button variant="primary" type="submit" className="w-full mt-[12px]" disabled={loading}>
            {loading ? (slow ? "Waking the server…" : "Signing in...") : "Sign In"}
          </Button>

          {loading && slow && (
            <p role="status" className="text-center text-[12px] text-text-dim">
              The free server sleeps when idle — the first sign-in can take up to a minute.
            </p>
          )}

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs mt-2 text-center space-y-1.5">
              <div>{error}</div>
              {isUnverified && (
                <div className="pt-1">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={resending}
                    className="underline text-primary hover:text-primary/80 font-medium cursor-pointer"
                  >
                    {resending ? "Sending link..." : "Resend Verification Email"}
                  </button>
                  {resendNotice && <div className="text-emerald-400 mt-1">{resendNotice}</div>}
                </div>
              )}
            </div>
          )}
        </form>

        <div className="flex items-center gap-[16px] my-[24px]">
          <Divider className="flex-1" />
          <span className="text-[12px] font-mono tracking-[0.04em] text-text-dim uppercase">Or continue with</span>
          <Divider className="flex-1" />
        </div>

        <SocialAuth disabled={loading} onError={setError} />

        <div className="mt-[28px] text-center">
          <Button variant="ghost" className="w-full text-text-mid group" onClick={handleGuestLogin} disabled={loading}>
            <UserRound className="w-[16px] h-[16px] mr-[6px]" />
            Continue as guest
            <ArrowRight className="w-[14px] h-[14px] ml-[4px] opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
          </Button>
        </div>
        
        <div className="mt-[24px] text-center text-[12px] text-text-dim">
          By continuing, you agree to our <Link href="/terms" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Terms</Link> & <Link href="/privacy" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Privacy</Link>
        </div>

        <div className="mt-[16px] text-center text-[13px] text-text-dim">
          Don't have an account?{" "}
          <Link href="/signup" className="text-signal-400 hover:text-signal-300 transition-colors font-medium">
            Sign Up
          </Link>
        </div>
      </Card>

    </>
  );
}
