/**
 * WEBISCRAP Interface Sound Manager
 *
 * Generates all sounds synthetically via the Web Audio API — zero external dependencies,
 * zero network requests, and zero extra bundle weight. Each sound is a short synthesised
 * tone tuned to the futuristic HUD aesthetic of the application.
 *
 * Sounds are opt-in and respect the user's preference stored in localStorage
 * ("webiscrap_sounds_enabled" = "true" | "false").
 *
 * Usage:
 *   const sound = useSound();
 *   sound.play("click");
 */

"use client";

import { useCallback, useRef } from "react";

export type SoundName =
  | "click"         // light UI tap — buttons, nav items
  | "success"       // operation completed — scrape done, save done
  | "error"         // operation failed
  | "open"          // modal / panel opened
  | "close"         // modal / panel closed
  | "notify"        // notification / info banner appears
  | "logout";       // session ended

const SOUNDS_KEY = "webiscrap_sounds_enabled";

// ─── Synthesis helpers ────────────────────────────────────────────────────────

function getCtx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  try {
    const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctx) return null;
    return new Ctx();
  } catch {
    return null;
  }
}

/** Very short fade-out to prevent clicks/pops on every note. */
function fadeOut(gain: GainNode, ctx: AudioContext, startAt: number, duration: number) {
  gain.gain.setValueAtTime(gain.gain.value, startAt);
  gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);
}

function playTone(
  ctx: AudioContext,
  opts: {
    freq: number;
    type?: OscillatorType;
    gain?: number;
    start?: number;
    duration?: number;
    detune?: number;
  }
) {
  const { freq, type = "sine", gain = 0.18, start = 0, duration = 0.12, detune = 0 } = opts;
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  osc.detune.value = detune;
  g.gain.value = gain;
  osc.connect(g);
  g.connect(ctx.destination);
  osc.start(ctx.currentTime + start);
  fadeOut(g, ctx, ctx.currentTime + start, duration);
  osc.stop(ctx.currentTime + start + duration + 0.02);
}

// ─── Sound definitions ────────────────────────────────────────────────────────

const synthesise: Record<SoundName, (ctx: AudioContext) => void> = {
  click(ctx) {
    playTone(ctx, { freq: 880, type: "sine", gain: 0.10, duration: 0.06 });
  },

  success(ctx) {
    playTone(ctx, { freq: 523.25, type: "sine", gain: 0.14, duration: 0.14, start: 0 });
    playTone(ctx, { freq: 659.25, type: "sine", gain: 0.14, duration: 0.18, start: 0.10 });
  },

  error(ctx) {
    playTone(ctx, { freq: 330, type: "sawtooth", gain: 0.09, duration: 0.12, start: 0 });
    playTone(ctx, { freq: 261, type: "sawtooth", gain: 0.09, duration: 0.15, start: 0.09 });
  },

  open(ctx) {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(420, ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(680, ctx.currentTime + 0.12);
    g.gain.value = 0.11;
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(ctx.currentTime);
    fadeOut(g, ctx, ctx.currentTime, 0.16);
    osc.stop(ctx.currentTime + 0.20);
  },

  close(ctx) {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(680, ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(350, ctx.currentTime + 0.10);
    g.gain.value = 0.10;
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(ctx.currentTime);
    fadeOut(g, ctx, ctx.currentTime, 0.12);
    osc.stop(ctx.currentTime + 0.16);
  },

  notify(ctx) {
    playTone(ctx, { freq: 780, type: "sine", gain: 0.12, duration: 0.20 });
  },

  logout(ctx) {
    playTone(ctx, { freq: 440, type: "sine", gain: 0.12, duration: 0.12, start: 0 });
    playTone(ctx, { freq: 330, type: "sine", gain: 0.10, duration: 0.12, start: 0.10 });
    playTone(ctx, { freq: 220, type: "sine", gain: 0.08, duration: 0.18, start: 0.20 });
  },
};

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useSound() {
  const enabledRef = useRef<boolean | null>(null);

  const isEnabled = useCallback((): boolean => {
    if (enabledRef.current !== null) return enabledRef.current;
    try {
      const stored = localStorage.getItem(SOUNDS_KEY);
      const val = stored === null ? true : stored === "true";
      enabledRef.current = val;
      return val;
    } catch {
      return false;
    }
  }, []);

  const play = useCallback(
    (name: SoundName) => {
      if (!isEnabled()) return;
      const ctx = getCtx();
      if (!ctx) return;
      try {
        synthesise[name](ctx);
        setTimeout(() => ctx.close().catch(() => {}), 800);
      } catch {
        // Never throw — sounds are a non-critical enhancement
      }
    },
    [isEnabled]
  );

  const setEnabled = useCallback((enabled: boolean) => {
    enabledRef.current = enabled;
    try { localStorage.setItem(SOUNDS_KEY, String(enabled)); } catch { /* ignore */ }
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("webiscrap_sounds_toggle", { detail: { enabled } }));
    }
  }, []);

  return { play, setEnabled, isEnabled };
}
