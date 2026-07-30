"use client";

import Image from "next/image";
import { useState } from "react";
import { Globe2, Phone, UserCircle, ArrowRight, Loader2 } from "lucide-react";

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleLogin = (provider: string) => {
    setIsLoading(provider);
    // Simulate — in production this calls the backend auth endpoints
    setTimeout(() => {
      setIsLoading(null);
      window.location.href = "/";
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-[#0a0a0a]">
        {/* Subtle gradient orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/3 rounded-full blur-3xl" />
      </div>

      {/* Glass Card */}
      <div className="relative z-10 glass-card w-full max-w-sm mx-4 p-8">
        {/* Branding */}
        <div className="flex flex-col items-center mb-8">
          <Image
            src="/assets/branding-logo.png"
            alt="WEBISCRAP"
            width={64}
            height={64}
            className="rounded-xl mb-4"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
            }}
          />
          <h1 className="text-xl font-semibold text-foreground">
            Welcome to WEBISCRAP
          </h1>
          <p className="text-sm text-muted mt-1 text-center">
            Sign in to start extracting data
          </p>
        </div>

        {/* Auth Options */}
        <div className="space-y-3">
          {/* Google OAuth */}
          <button
            onClick={() => handleLogin("google")}
            disabled={isLoading !== null}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-sm text-foreground cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading === "google" ? (
              <Loader2 className="w-5 h-5 animate-spin-slow" />
            ) : (
              <Globe2 className="w-5 h-5" />
            )}
            <span className="flex-1 text-left">Continue with Google</span>
            <ArrowRight className="w-4 h-4 text-muted" />
          </button>

          {/* Phone OTP */}
          <button
            onClick={() => handleLogin("phone")}
            disabled={isLoading !== null}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-sm text-foreground cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading === "phone" ? (
              <Loader2 className="w-5 h-5 animate-spin-slow" />
            ) : (
              <Phone className="w-5 h-5" />
            )}
            <span className="flex-1 text-left">Continue with Phone</span>
            <ArrowRight className="w-4 h-4 text-muted" />
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 py-1">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-xs text-muted">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Guest Mode */}
          <button
            onClick={() => handleLogin("guest")}
            disabled={isLoading !== null}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-primary/10 border border-primary/20 hover:bg-primary/15 transition-colors text-sm text-foreground cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading === "guest" ? (
              <Loader2 className="w-5 h-5 animate-spin-slow" />
            ) : (
              <UserCircle className="w-5 h-5" />
            )}
            <span className="flex-1 text-left">Continue as Guest</span>
            <ArrowRight className="w-4 h-4 text-muted" />
          </button>
        </div>

        {/* Footer */}
        <p className="text-[11px] text-muted text-center mt-6">
          By continuing, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}
