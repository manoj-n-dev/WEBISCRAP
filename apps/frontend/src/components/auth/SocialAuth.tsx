"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Script from "next/script";
import { useRouter } from "next/navigation";
import { Phone } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ApiClient } from "@/lib/api/client";
import { useChatStore } from "@/lib/store/chat";
import { formatFirebaseAuthError, signInWithGooglePopup } from "@/lib/firebase";

interface GoogleCredentialResponse { credential?: string }
interface GoogleIdApi {
  initialize: (cfg: { client_id: string; callback: (r: GoogleCredentialResponse) => void; ux_mode?: string; auto_select?: boolean }) => void;
  renderButton: (el: HTMLElement, opts: Record<string, unknown>) => void;
}
declare global {
  interface Window { google?: { accounts: { id: GoogleIdApi } } }
}

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

export interface SocialAuthProps {
  disabled?: boolean;
  onError: (message: string | null) => void;
}

/**
 * Google sign-in via Google Identity Services (only the PUBLIC OAuth client id is used — no Firebase API key appears
 * in any URL) with a lazy Firebase fallback, plus the Phone OTP option which currently shows "not available for now".
 */
export function SocialAuth({ disabled, onError }: SocialAuthProps) {
  const router = useRouter();
  const buttonRef = useRef<HTMLDivElement>(null);
  const [gsiReady, setGsiReady] = useState(false);
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

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || !gsiReady || !buttonRef.current || !window.google) return;
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: (r) => { if (r.credential) void finish(r.credential); },
    });
    const width = Math.min(400, Math.max(200, buttonRef.current.clientWidth || 320));
    window.google.accounts.id.renderButton(buttonRef.current, { type: "standard", theme: "filled_black", size: "large", shape: "pill", text: "continue_with", width, logo_alignment: "left" });
  }, [gsiReady, finish]);

  const firebaseFallback = async () => {
    setBusy(true);
    onError(null);
    try {
      await finish(await signInWithGooglePopup());
    } catch (e) {
      const msg = formatFirebaseAuthError(e);
      if (msg) onError(msg);
      setBusy(false);
    }
  };

  const off = disabled || busy;
  return (
    <div className="flex flex-col gap-[12px]">
      {GOOGLE_CLIENT_ID ? (
        <>
          <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" onLoad={() => setGsiReady(true)} onReady={() => setGsiReady(true)} />
          <div ref={buttonRef} className={`w-full flex justify-center min-h-[44px] ${off ? "pointer-events-none opacity-60" : ""}`} aria-label="Continue with Google" />
        </>
      ) : (
        <Button onClick={firebaseFallback} disabled={off} className="w-full justify-start pl-[20px]">
          <GoogleGlyph />
          Google
        </Button>
      )}

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
