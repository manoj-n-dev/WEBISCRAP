"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Phone } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ApiClient } from "@/lib/api/client";
import { useChatStore } from "@/lib/store/chat";
import { formatFirebaseAuthError, isFirebaseConfigured, signInWithGoogleRedirect, getGoogleRedirectResult } from "@/lib/firebase";

export interface SocialAuthProps {
  disabled?: boolean;
  onError: (message: string | null) => void;
}

/**
 * Google sign-in via Firebase OAuth Redirect (navigates current tab to Google Accounts, no popups)
 * with automatic redirect token resolution on page mount.
 */
export function SocialAuth({ disabled, onError }: SocialAuthProps) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [phoneNotice, setPhoneNotice] = useState(false);

  const finish = useCallback(async (idToken: string) => {
    setBusy(true);
    onError(null);
    try {
      const response = await ApiClient.googleLogin(idToken);
      if (response.access_token) {
        useChatStore.getState().resetAll();
        ApiClient.setToken(response.access_token);
        router.push("/chat/new");
      }
    } catch (e) {
      onError(e instanceof Error ? e.message : "Google sign-in failed");
    } finally {
      setBusy(false);
    }
  }, [onError, router]);

  // Listen for Google OAuth redirect callback on page mount
  useEffect(() => {
    let isMounted = true;
    const checkRedirect = async () => {
      if (!isFirebaseConfigured()) return;
      try {
        const token = await getGoogleRedirectResult();
        if (token && isMounted) {
          await finish(token);
        }
      } catch (e) {
        if (isMounted) {
          const msg = formatFirebaseAuthError(e);
          if (msg) onError(msg);
        }
      }
    };
    void checkRedirect();
    return () => {
      isMounted = false;
    };
  }, [finish, onError]);

  const handleGoogleSignIn = async () => {
    setBusy(true);
    onError(null);
    try {
      await signInWithGoogleRedirect();
    } catch (e) {
      const msg = formatFirebaseAuthError(e);
      if (msg) onError(msg);
      setBusy(false);
    }
  };

  const off = disabled || busy;
  return (
    <div className="flex flex-col gap-[12px]">
      <Button onClick={handleGoogleSignIn} disabled={off} className="w-full justify-start pl-[20px]">
        <GoogleGlyph />
        {busy ? "Redirecting to Google..." : "Google"}
      </Button>

      <Button
        onClick={() => { setPhoneNotice(true); onError(null); }}
        disabled={off}
        aria-describedby={phoneNotice ? "phone-otp-notice" : undefined}
        className="w-full justify-start pl-[20px]"
      >
        <Phone className="w-[18px] h-[18px] mr-[8px] opacity-80" />
        Phone OTP
        <span className="ml-auto pr-[6px] font-mono text-[10px] uppercase tracking-[0.08em] text-text-dim">Soon</span>
      </Button>
      {phoneNotice && (
        <p id="phone-otp-notice" role="status" className="rounded-lg border border-hair bg-white/5 px-[12px] py-[10px] text-[12.5px] text-text-mid text-center">
          Phone OTP sign-in is not available for now. Please use email, Google, or continue as a guest.
        </p>
      )}
    </div>
  );
}

function GoogleGlyph() {
  return (
    <svg className="w-[18px] h-[18px] mr-[8px] opacity-80" viewBox="0 0 24 24" aria-hidden>
      <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}
