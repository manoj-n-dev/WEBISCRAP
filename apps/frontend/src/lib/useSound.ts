/**
 * WEBISCRAP Interface Sound Manager
 *
 * Generates all sounds synthetically via the Web Audio API — zero external dependencies,
 * zero network requests, and zero extra bundle weight. Each sound is a short synthesised
 * tone tuned to the futuristic HUD aesthetic of the application.
 *
 * Sounds are opt-in and respect the user's preference stored in localStorage
 * ("webiscrap_sounds_enabled" = "true" | "false", defaults to true).
 *
 * Usage in React components:
 *   const sound = useSound();
 *   sound.play("click");
 *   sound.playTyping();
 *
 * Usage outside React (e.g. stores, export helpers):
 *   playInterfaceSound("download");
 */

"use client";

import { useCallback, useRef } from "react";

export type SoundName =
  | "click"             // light UI tap — buttons, nav items
  | "success"           // operation completed — save done
  | "error"             // operation failed
  | "open"              // modal / panel opened
  | "close"             // modal / panel closed
  | "notify"            // notification / info banner appears
  | "logout"            // session ended
  | "login"             // session established / logged in
  | "upload"            // file upload started / file dropped
  | "upload_done"       // file upload processed & ready
  | "extraction_start"  // extraction pipeline initiated
  | "extraction_done"   // extraction completed with dataset
  | "download"          // dataset exported / downloaded
  | "typing";           // subtle keystroke click

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

/** Check whether interface sounds are enabled in localStorage. */
export function areSoundsEnabled(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const stored = localStorage.getItem(SOUNDS_KEY);
    return stored === null ? true : stored === "true";
  } catch {
    return false;
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

  login(ctx) {
    // Upbeat 4-note ascending major chime
    playTone(ctx, { freq: 523.25, type: "sine", gain: 0.11, duration: 0.10, start: 0 });
    playTone(ctx, { freq: 659.25, type: "sine", gain: 0.12, duration: 0.11, start: 0.07 });
    playTone(ctx, { freq: 783.99, type: "sine", gain: 0.13, duration: 0.13, start: 0.14 });
    playTone(ctx, { freq: 1046.50, type: "sine", gain: 0.15, duration: 0.22, start: 0.21 });
  },

  upload(ctx) {
    // Futuristic rising synth sweep
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(320, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(840, ctx.currentTime + 0.18);
    g.gain.value = 0.11;
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(ctx.currentTime);
    fadeOut(g, ctx, ctx.currentTime, 0.18);
    osc.stop(ctx.currentTime + 0.22);
  },

  upload_done(ctx) {
    // Crisp dual-tone confirmation chime
    playTone(ctx, { freq: 587.33, type: "sine", gain: 0.11, duration: 0.09, start: 0 });
    playTone(ctx, { freq: 880.00, type: "sine", gain: 0.13, duration: 0.16, start: 0.07 });
  },

  extraction_start(ctx) {
    // High-tech scanner engagement pulse
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.09);
    osc.frequency.linearRampToValueAtTime(660, ctx.currentTime + 0.18);
    g.gain.value = 0.10;
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(ctx.currentTime);
    fadeOut(g, ctx, ctx.currentTime, 0.19);
    osc.stop(ctx.currentTime + 0.24);
  },

  extraction_done(ctx) {
    // Triumphant HUD mission-complete melodic chord
    playTone(ctx, { freq: 440.00, type: "sine", gain: 0.11, duration: 0.14, start: 0 });
    playTone(ctx, { freq: 554.37, type: "sine", gain: 0.12, duration: 0.16, start: 0.08 });
    playTone(ctx, { freq: 659.25, type: "sine", gain: 0.13, duration: 0.20, start: 0.15 });
    playTone(ctx, { freq: 880.00, type: "sine", gain: 0.15, duration: 0.28, start: 0.22 });
  },

  download(ctx) {
    // Elegant cascading download sweep
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(780, ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(480, ctx.currentTime + 0.09);
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.20);
    g.gain.value = 0.12;
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(ctx.currentTime);
    fadeOut(g, ctx, ctx.currentTime, 0.21);
    osc.stop(ctx.currentTime + 0.25);
  },

  typing(ctx) {
    // Ultra-subtle tactile mechanical keystroke click
    const pitch = 1300 + Math.random() * 200;
    playTone(ctx, { freq: pitch, type: "sine", gain: 0.024, duration: 0.015 });
  },
};

// ─── Standalone non-React sound trigger ────────────────────────────────────────

let lastTypingTime = 0;

/** Play an interface sound from anywhere (inside or outside React). */
export function playInterfaceSound(name: SoundName) {
  if (!areSoundsEnabled()) return;

  // Rate-limit typing sounds so holding a key or rapid typing stays pleasant and non-distorted
  if (name === "typing") {
    const now = Date.now();
    if (now - lastTypingTime < 45) return;
    lastTypingTime = now;
  }

  const ctx = getCtx();
  if (!ctx) return;
  try {
    synthesise[name](ctx);
    setTimeout(() => ctx.close().catch(() => {}), 900);
  } catch {
    // Never throw — audio is purely enhancement
  }
}

// ─── React Hook ───────────────────────────────────────────────────────────────

export function useSound() {
  const enabledRef = useRef<boolean | null>(null);

  const isEnabled = useCallback((): boolean => {
    if (enabledRef.current !== null) return enabledRef.current;
    const val = areSoundsEnabled();
    enabledRef.current = val;
    return val;
  }, []);

  const play = useCallback((name: SoundName) => {
    playInterfaceSound(name);
  }, []);

  const playTyping = useCallback(() => {
    playInterfaceSound("typing");
  }, []);

  const setEnabled = useCallback((enabled: boolean) => {
    enabledRef.current = enabled;
    try { localStorage.setItem(SOUNDS_KEY, String(enabled)); } catch { /* ignore */ }
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("webiscrap_sounds_toggle", { detail: { enabled } }));
    }
  }, []);

  return { play, playTyping, setEnabled, isEnabled };
}
