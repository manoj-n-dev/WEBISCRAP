"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Lock, CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";
import { ApiClient } from "@/lib/api/client";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return "Password must be at least 8 characters long";
    if (!/[A-Z]/.test(pwd)) return "Password must contain at least one uppercase letter";
    if (!/[0-9]/.test(pwd)) return "Password must contain at least one number";
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setStatus("error");
      setErrorMessage("Reset token is missing from the link. Please request a new link.");
      return;
    }

    const pwdError = validatePassword(password);
    if (pwdError) {
      setStatus("error");
      setErrorMessage(pwdError);
      return;
    }

    if (password !== confirmPassword) {
      setStatus("error");
      setErrorMessage("Passwords do not match");
      return;
    }

    setStatus("loading");
    setErrorMessage("");

    try {
      await ApiClient.resetPassword(token, password);
      setStatus("success");
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err.message || "Failed to reset password. The link may have expired.");
    }
  };

  if (!token) {
    return (
      <Card variant="strong" className="p-[32px] w-full max-w-md mx-auto text-center">
        <div className="w-[48px] h-[48px] rounded-full bg-red-500/10 text-red-500 flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h1 className="text-[20px] font-display font-semibold mb-[8px]">Invalid Reset Link</h1>
        <p className="text-[14px] text-text-dim mb-6">
          This password reset link is missing a valid security token. Please request a new password reset link.
        </p>
        <Button variant="primary" className="w-full" onClick={() => router.push("/forgot-password")}>
          Request new reset link
        </Button>
      </Card>
    );
  }

  return (
    <Card variant="strong" className="p-[32px] animate-in fade-in slide-in-from-bottom-4 duration-500 w-full max-w-md mx-auto">
      <div className="text-center mb-[28px]">
        <h1 className="text-[24px] font-display font-semibold mb-[8px]">Create new password</h1>
        <p className="text-[14px] text-text-dim">Your new password must be different from previous passwords.</p>
      </div>

      {status === "success" ? (
        <div className="text-center">
          <div className="w-[48px] h-[48px] rounded-full bg-green-500/10 text-green-500 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-medium text-text-hi mb-2">Password reset complete</h3>
          <p className="text-text-dim mb-6 text-sm">
            Your password has been successfully updated. You can now log in with your new credentials.
          </p>
          <Button variant="primary" className="w-full" onClick={() => router.push("/login")}>
            Proceed to login
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-[20px]">
          <div>
            <label className="text-sm text-text-dim mb-1 block">New password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              icon={<Lock className="w-[16px] h-[16px]" />}
              showPasswordToggle={true}
              required
              disabled={status === "loading"}
            />
            <span className="text-[11px] text-text-dim mt-1 block">
              Must be at least 8 characters with 1 uppercase letter and 1 number.
            </span>
          </div>

          <div>
            <label className="text-sm text-text-dim mb-1 block">Confirm new password</label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              icon={<Lock className="w-[16px] h-[16px]" />}
              showPasswordToggle={true}
              required
              disabled={status === "loading"}
            />
          </div>

          {status === "error" && (
            <div className="text-red-500 text-sm p-3 rounded bg-red-500/10 border border-red-500/20 text-center">
              {errorMessage}
            </div>
          )}

          <Button
            variant="primary"
            type="submit"
            className="w-full h-[44px]"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Updating password..." : "Update password"}
          </Button>

          <div className="text-center mt-2">
            <Link href="/login" className="text-[13px] text-text-dim hover:text-text-hi transition-colors">
              Back to login
            </Link>
          </div>
        </form>
      )}
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="text-center text-text-dim">Loading reset form...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
