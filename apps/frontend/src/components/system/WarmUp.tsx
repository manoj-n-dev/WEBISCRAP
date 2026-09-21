"use client";

import { useEffect } from "react";
import { warmUpBackend } from "@/lib/warmup";

/** Invisible. Fires a cheap /health request as soon as any page opens so a sleeping backend starts booting immediately. */
export function WarmUp() {
  useEffect(() => {
    warmUpBackend();
  }, []);
  return null;
}
