"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Divider } from "@/components/ui/Divider";
import { Mail, Lock, Phone, UserRound, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    router.push("/chat/new");
  };

  return (
    <Card variant="strong" className="p-[32px] animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center mb-[28px]">
        <h1 className="text-[24px] font-display font-semibold mb-[8px]">Welcome Back</h1>
        <p className="text-[14px] text-text-dim">Sign in to access your extractions</p>
      </div>

      <form onSubmit={handleLogin} className="flex flex-col gap-[16px]">
        <Input 
          type="email" 
          placeholder="Email address" 
          icon={<Mail className="w-[16px] h-[16px]" />} 
          required 
        />
        
        <Input 
          type="password" 
          placeholder="Password" 
          icon={<Lock className="w-[16px] h-[16px]" />} 
          required 
        />
        
        <div className="flex items-center justify-between mt-[4px]">
          <label className="flex items-center gap-[8px] cursor-pointer group">
            <div className="w-[16px] h-[16px] rounded-[4px] border border-glass-border-strong group-hover:border-signal-300 transition-colors flex items-center justify-center">
              <svg className="w-[10px] h-[10px] text-transparent transition-colors group-[.is-checked]:text-signal-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <span className="text-[13px] text-text-mid group-hover:text-text-hi transition-colors">Stay signed in</span>
          </label>
          <a href="#" className="text-[13px] text-signal-400 hover:text-signal-300 transition-colors">
            Forgot password?
          </a>
        </div>
        
        <Button variant="primary" type="submit" className="w-full mt-[12px]">
          Sign In
        </Button>
      </form>

      <div className="flex items-center gap-[16px] my-[24px]">
        <Divider className="flex-1" />
        <span className="text-[12px] font-mono tracking-[0.04em] text-text-dim uppercase">Or continue with</span>
        <Divider className="flex-1" />
      </div>

      <div className="flex flex-col gap-[12px]">
        <Button className="w-full justify-start pl-[20px] bg-white/5 border-glass-border-strong text-text-hi hover:bg-white/10 hover:border-glass-border-strong hover:text-white group">
          <svg className="w-[18px] h-[18px] mr-[8px] opacity-80 group-hover:opacity-100 transition-opacity" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          Google
        </Button>
        <Button className="w-full justify-start pl-[20px] bg-white/5 border-glass-border-strong text-text-hi hover:bg-white/10 hover:border-glass-border-strong hover:text-white group">
          <Phone className="w-[18px] h-[18px] mr-[8px] opacity-80 group-hover:opacity-100 transition-opacity" />
          Phone OTP
        </Button>
      </div>

      <div className="mt-[28px] text-center">
        <Link href="/chat/new">
          <Button variant="ghost" className="w-full text-text-mid group">
            <UserRound className="w-[16px] h-[16px] mr-[6px]" />
            Continue as guest
            <ArrowRight className="w-[14px] h-[14px] ml-[4px] opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
          </Button>
        </Link>
      </div>
      
      <div className="mt-[24px] text-center text-[12px] text-text-dim">
        By continuing, you agree to our <a href="#" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Terms</a> & <a href="#" className="text-text-mid hover:text-text-hi transition-colors underline decoration-hair underline-offset-4">Privacy</a>
      </div>
    </Card>
  );
}
