"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { Mail, Lock, Phone, X } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { auth, googleProvider, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber } from "@/lib/firebase";

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Phone OTP state
  const [showPhoneModal, setShowPhoneModal] = React.useState(false);
  const [phoneNumber, setPhoneNumber] = React.useState("");
  const [otpSent, setOtpSent] = React.useState(false);
  const [otp, setOtp] = React.useState("");
  const [confirmationResult, setConfirmationResult] = React.useState<any>(null);

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return "Password must be at least 8 characters";
    if (!/[A-Z]/.test(pwd)) return "Password must contain at least one uppercase letter";
    if (!/[0-9]/.test(pwd)) return "Password must contain at least one number";
    return null;
  };

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
      // 1. Register the user
      await ApiClient.register(email, password);
      
      // 2. Log them in to get the token
      const response = await ApiClient.login(email, password);
      
      if (response.access_token) {
        localStorage.setItem("token", response.access_token);
        router.push("/chat/new");
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign up");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const idToken = await result.user.getIdToken();
      const response = await ApiClient.googleLogin(idToken);
      if (response.access_token) {
        localStorage.setItem("token", response.access_token);
        router.push("/chat/new");
      }
    } catch (err: any) {
      if (err.code === "auth/popup-closed-by-user") return;
      setError(err.message || "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSendOTP = async () => {
    if (!phoneNumber.trim()) {
      setError("Enter a valid phone number with country code (e.g. +91...)");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const recaptchaContainer = document.getElementById("recaptcha-container");
      if (!recaptchaContainer) return;
      
      const verifier = new RecaptchaVerifier(auth, recaptchaContainer, { size: "invisible" });
      const confirmation = await signInWithPhoneNumber(auth, phoneNumber, verifier);
      setConfirmationResult(confirmation);
      setOtpSent(true);
    } catch (err: any) {
      setError(err.message || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp.trim() || !confirmationResult) return;
    setLoading(true);
    setError(null);
    try {
      const result = await confirmationResult.confirm(otp);
      const idToken = await result.user.getIdToken();
      const response = await ApiClient.phoneLogin(idToken);
      if (response.access_token) {
        localStorage.setItem("token", response.access_token);
        router.push("/chat/new");
      }
    } catch (err: any) {
      setError(err.message || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div id="recaptcha-container"></div>
      <Card variant="strong" className="p-[32px] animate-in fade-in slide-in-from-bottom-4 duration-500">
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

        <div className="flex flex-col gap-[12px]">
          <Button 
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full justify-start pl-[20px] bg-white/5 border-glass-border-strong text-text-hi hover:bg-white/10 hover:border-glass-border-strong hover:text-white group"
          >
            <svg className="w-[18px] h-[18px] mr-[8px] opacity-80 group-hover:opacity-100 transition-opacity" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Google
          </Button>
          <Button 
            onClick={() => { setShowPhoneModal(true); setError(null); }}
            disabled={loading}
            className="w-full justify-start pl-[20px] bg-white/5 border-glass-border-strong text-text-hi hover:bg-white/10 hover:border-glass-border-strong hover:text-white group"
          >
            <Phone className="w-[18px] h-[18px] mr-[8px] opacity-80 group-hover:opacity-100 transition-opacity" />
            Phone OTP
          </Button>
        </div>

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

      {/* Phone OTP Modal */}
      {showPhoneModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <Card variant="strong" className="p-[32px] w-[400px] animate-in fade-in zoom-in-95 duration-200 relative">
            <button 
              onClick={() => { setShowPhoneModal(false); setOtpSent(false); setOtp(""); setPhoneNumber(""); }}
              className="absolute top-[16px] right-[16px] text-text-dim hover:text-text-hi transition-colors cursor-pointer"
            >
              <X className="w-[18px] h-[18px]" />
            </button>
            <h2 className="text-[20px] font-display font-semibold mb-[8px]">Phone Login</h2>
            <p className="text-[13px] text-text-dim mb-[20px]">
              {otpSent ? "Enter the OTP sent to your phone." : "Enter your phone number with country code."}
            </p>

            {!otpSent ? (
              <div className="flex flex-col gap-[14px]">
                <Input
                  type="tel"
                  placeholder="+91 9876543210"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  icon={<Phone className="w-[16px] h-[16px]" />}
                  disabled={loading}
                />
                <Button variant="primary" className="w-full" onClick={handleSendOTP} disabled={loading}>
                  {loading ? "Sending..." : "Send OTP"}
                </Button>
              </div>
            ) : (
              <div className="flex flex-col gap-[14px]">
                <Input
                  type="text"
                  placeholder="Enter 6-digit OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  icon={<Lock className="w-[16px] h-[16px]" />}
                  disabled={loading}
                />
                <Button variant="primary" className="w-full" onClick={handleVerifyOTP} disabled={loading}>
                  {loading ? "Verifying..." : "Verify OTP"}
                </Button>
              </div>
            )}
            {error && <div className="text-red-500 text-sm mt-3 text-center">{error}</div>}
          </Card>
        </div>
      )}
    </>
  );
}
