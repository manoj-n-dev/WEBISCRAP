"use client";

import React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { CheckCircle2, AlertCircle, Mail, ArrowRight, Loader2 } from "lucide-react";
import { ApiClient } from "@/lib/api/client";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = React.useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = React.useState<string>("");
  const [resendEmail, setResendEmail] = React.useState<string>("");
  const [resending, setResending] = React.useState<boolean>(false);
  const [resendSuccess, setResendSuccess] = React.useState<string | null>(null);
  const [resendError, setResendError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token. Please check the link from your email.");
      return;
    }

    let isMounted = true;
    const verify = async () => {
      setStatus("loading");
      try {
        const res: any = await ApiClient.verifyEmail(token);
        if (isMounted) {
          setStatus("success");
          setMessage(res.message || "Your email address has been verified successfully!");
        }
      } catch (err: any) {
        if (isMounted) {
          setStatus("error");
          setMessage(err.message || "Invalid, expired, or already used verification token.");
        }
      }
    };

    verify();
    return () => {
      isMounted = false;
    };
  }, [token]);

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resendEmail) return;
    setResending(true);
    setResendSuccess(null);
    setResendError(null);
    try {
      const res: any = await ApiClient.resendVerification(resendEmail);
      setResendSuccess(res.message || "A new verification email has been sent if the account exists.");
    } catch (err: any) {
      setResendError(err.message || "Failed to resend verification email. Please wait before trying again.");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 border border-white/10 bg-[#161b22]/90 backdrop-blur-md shadow-2xl text-center">
        {status === "loading" && (
          <div className="flex flex-col items-center py-6 space-y-4">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <h2 className="text-xl font-bold text-white">Verifying your email</h2>
            <p className="text-sm text-muted-foreground">
              Please wait while we confirm your account credentials...
            </p>
          </div>
        )}

        {status === "success" && (
          <div className="flex flex-col items-center py-6 space-y-4">
            <div className="w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-white">Email Verified!</h2>
            <p className="text-sm text-muted-foreground max-w-xs">{message}</p>
            <div className="pt-4 w-full">
              <Link href="/login" className="w-full block">
                <Button className="w-full flex items-center justify-center gap-2">
                  Proceed to Login <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="flex flex-col items-center py-4 space-y-4 text-left">
            <div className="w-12 h-12 rounded-full bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400 mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div className="text-center w-full">
              <h2 className="text-lg font-bold text-white">Verification Link Issue</h2>
              <p className="text-sm text-rose-400/90 mt-1">{message}</p>
            </div>

            <div className="w-full mt-4 p-4 rounded-lg bg-black/30 border border-white/5 space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-primary" /> Request a New Link
              </h3>
              <form onSubmit={handleResend} className="space-y-3">
                <Input
                  type="email"
                  placeholder="Enter your registered email"
                  value={resendEmail}
                  onChange={(e) => setResendEmail(e.target.value)}
                  required
                  className="bg-black/40 border-white/10 text-sm"
                />
                <Button
                  type="submit"
                  disabled={resending || !resendEmail}
                  className="w-full text-xs h-9"
                >
                  {resending ? "Sending..." : "Resend Verification Email"}
                </Button>
              </form>

              {resendSuccess && (
                <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
                  {resendSuccess}
                </div>
              )}
              {resendError && (
                <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                  {resendError}
                </div>
              )}
            </div>

            <div className="pt-2 w-full text-center">
              <Link
                href="/login"
                className="text-xs text-muted-foreground hover:text-white transition-colors"
              >
                Back to Sign In
              </Link>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
