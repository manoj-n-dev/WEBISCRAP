"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { Mail, Lock, Wand2 } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { SocialAuth } from "@/components/auth/SocialAuth";

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return "Password must be at least 8 characters";
    if (!/[A-Z]/.test(pwd)) return "Password must contain at least one uppercase letter";
    if (!/[0-9]/.test(pwd)) return "Password must contain at least one number";
    return null;
  };

  const [signupSuccess, setSignupSuccess] = React.useState(false);
  const [emailSent, setEmailSent] = React.useState(true);
  const [resendStatus, setResendStatus] = React.useState<string | null>(null);
  const [resending, setResending] = React.useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      // 1. Register the user (creates unverified account & dispatches verification email)
      const res: any = await ApiClient.register(email, password);
      setEmailSent(res?.email_sent !== false);
      setSignupSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to sign up");
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResending(true);
    setResendStatus(null);
    try {
      const res: any = await ApiClient.resendVerification(email);
      setResendStatus(res.message || "Verification email resent successfully.");
    } catch (err: any) {
      setResendStatus(err.message || "Failed to resend. Please try again in a few minutes.");
    } finally {
      setResending(false);
    }
  };

  if (signupSuccess) {
    return (
      <Card variant="strong" className="p-[22px] sm:p-[32px] animate-in text-center max-w-md mx-auto">
        <div className="w-14 h-14 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary mx-auto mb-5">
          <Mail className="w-7 h-7" />
        </div>
        <h1 className="text-[22px] font-display font-semibold mb-[8px] text-white">Check Your Inbox</h1>
        <p className="text-[14px] text-text-dim mb-[24px]">
          {emailSent ? (
            <>We sent a verification email to <strong className="text-white">{email}</strong>. Click the link in it to activate your account. Check your spam folder too.</>
          ) : (
            <>Your account was created, but we couldn&apos;t send the verification email to <strong className="text-white">{email}</strong> right now. Tap &ldquo;Resend Verification Email&rdquo; below in a moment.</>
          )}
        </p>

        <div className="flex flex-col gap-3">
          <Link href="/login" className="w-full">
            <Button className="w-full">Go to Sign In</Button>
          </Link>
          <Button
            variant="ghost"
            onClick={handleResendVerification}
            disabled={resending}
            className="w-full text-xs"
          >
            {resending ? "Sending..." : "Resend Verification Email"}
          </Button>
        </div>

        {resendStatus && (
          <p className="text-xs text-emerald-400 mt-4 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
            {resendStatus}
          </p>
        )}
      </Card>
    );
  }

  return (
    <>
      <Card variant="strong" className="p-[22px] sm:p-[32px] animate-in">
        <div className="text-center mb-[28px]">
          <h1 className="text-[24px] font-display font-semibold mb-[8px]">Create an Account</h1>
          <p className="text-[14px] text-text-dim">Join WEBISCRAP to start extracting data</p>
        </div>

        <form onSubmit={handleSignup} className="flex flex-col gap-[16px]">
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
            placeholder="Password (min 8 chars, 1 uppercase, 1 number)" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            icon={<Lock className="w-[16px] h-[16px]" />} 
            required 
            disabled={loading}
            rightElement={
              <button
                type="button"
                tabIndex={-1}
                onClick={() => {
                  const pick = (set: string) => set[crypto.getRandomValues(new Uint32Array(1))[0] % set.length];
                  const all = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
                  const chars = [pick("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), pick("abcdefghijklmnopqrstuvwxyz"), pick("0123456789"), pick("!@#$%^&*")];
                  for (let i = 0; i < 10; i++) chars.push(pick(all));
                  for (let i = chars.length - 1; i > 0; i--) {          // Fisher-Yates with a CSPRNG
                    const j = crypto.getRandomValues(new Uint32Array(1))[0] % (i + 1);
                    [chars[i], chars[j]] = [chars[j], chars[i]];
                  }
                  const pass = chars.join("");
                  setPassword(pass);
                  setConfirmPassword(pass);
                }}
                className="text-text-dim hover:text-signal-400 transition-colors flex items-center justify-center p-0.5 rounded hover:bg-white/5 cursor-pointer"
                title="Generate Strong Password"
                aria-label="Generate Strong Password"
              >
                <Wand2 className="w-[16px] h-[16px]" />
              </button>
            }
          />

          <Input 
            type="password" 
            placeholder="Confirm Password" 
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            icon={<Lock className="w-[16px] h-[16px]" />} 
            required 
            disabled={loading}
          />
          
          <Button variant="primary" type="submit" className="w-full mt-[12px]" disabled={loading}>
            {loading ? "Creating account..." : "Sign Up"}
          </Button>
          {error && <div className="text-red-500 text-sm mt-2 text-center">{error}</div>}
        </form>

        <div className="flex items-center gap-[16px] my-[24px]">
          <Divider className="flex-1" />
          <span className="text-[12px] font-mono tracking-[0.04em] text-text-dim uppercase">Or continue with</span>
          <Divider className="flex-1" />
        </div>

        <SocialAuth disabled={loading} onError={setError} />

        <div className="mt-[24px] text-center text-[12px] text-text-dim">
          By continuing, you agree to our <Link href="/terms" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Terms</Link> & <Link href="/privacy" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Privacy</Link>
        </div>

        <div className="mt-[16px] text-center text-[13px] text-text-dim">
          Already have an account?{" "}
          <Link href="/login" className="text-signal-400 hover:text-signal-300 transition-colors font-medium">
            Sign In
          </Link>
        </div>
      </Card>

    </>
  );
}
