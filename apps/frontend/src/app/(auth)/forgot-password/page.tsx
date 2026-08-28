"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ArrowRight, Mail } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setStatus("loading");
    setErrorMessage("");
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });
      if (!response.ok) {
        throw new Error("Failed to send reset email");
      }
      setStatus("success");
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err.message || "Failed to send reset email");
    }
  };

  return (
    <Card variant="strong" className="p-[32px] animate-in fade-in slide-in-from-bottom-4 duration-500 w-full max-w-md mx-auto">
      <div className="text-center mb-[28px]">
        <h1 className="text-[24px] font-display font-semibold mb-[8px]">Reset your password</h1>
        <p className="text-[14px] text-text-dim">Enter your email and we will send you instructions.</p>
      </div>

      {status === "success" ? (
        <div className="text-center">
          <div className="w-[48px] h-[48px] rounded-full bg-success/10 text-success flex items-center justify-center mx-auto mb-4">
            <Mail className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-medium text-text-hi mb-2">Check your email</h3>
          <p className="text-text-dim mb-6 text-sm">
            We have sent a password reset link to <span className="text-text-hi">{email}</span>.
          </p>
          <Button variant="ghost" className="w-full" onClick={() => window.location.href = "/login"}>
            Return to login
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-[20px]">
          <div>
            <label className="text-sm text-text-dim mb-1 block">Email address</label>
            <Input 
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              icon={<Mail className="w-[16px] h-[16px]" />}
              required
              disabled={status === "loading"}
            />
          </div>
          
          {status === "error" && (
            <div className="text-red-500 text-sm text-center">{errorMessage}</div>
          )}
          
          <Button 
            variant="primary"
            type="submit" 
            className="w-full h-[44px]"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Sending..." : "Send reset link"}
            {!status && <ArrowRight className="w-[16px] h-[16px] ml-2" />}
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
