"use client";

import React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { LimitReached } from "@/components/chat/LimitReached";

function LimitInner() {
  const params = useSearchParams();
  const retry = Number(params.get("retry")) || 60;
  const scope = params.get("scope") || "minute";
  return (
    <div className="max-w-[560px] mx-auto p-[16px] sm:p-[32px]">
      <LimitReached retryAfter={retry} scope={scope} />
      <Link href="/chat/new" className="inline-block mt-[16px]">
        <Button variant="ghost" className="text-[13px]"><ArrowLeft className="w-[15px] h-[15px]" />Back to chat</Button>
      </Link>
    </div>
  );
}

export default function LimitPage() {
  return (
    <React.Suspense fallback={null}>
      <LimitInner />
    </React.Suspense>
  );
}
