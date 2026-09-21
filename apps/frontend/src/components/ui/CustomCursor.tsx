"use client";

import React, { useEffect, useRef, useState } from "react";

export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isClicking, setIsClicking] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(true);

  useEffect(() => {
    // Only mount on devices with a fine pointer (desktop mouse/trackpad), not touch screens
    const hasFinePointer = window.matchMedia("(pointer: fine)").matches;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!hasFinePointer || prefersReducedMotion) {
      setIsTouchDevice(true);
      return;
    }
    setIsTouchDevice(false);

    let mouseX = -100;
    let mouseY = -100;
    let ringX = -100;
    let ringY = -100;
    let animId: number;

    const onMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      if (!visible) setVisible(true);

      // Instantly position the center dot
      if (dotRef.current) {
        dotRef.current.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
      }

      // Check if hovering over clickable element
      const target = e.target as HTMLElement | null;
      if (target) {
        const interactive = target.closest(
          'a, button, [role="button"], input, textarea, select, label, [tabindex="0"], summary'
        );
        setIsHovered(Boolean(interactive));
      }
    };

    const onMouseDown = () => setIsClicking(true);
    const onMouseUp = () => setIsClicking(false);

    const onMouseEnter = () => setVisible(true);
    const onMouseLeave = () => {
      setVisible(false);
      setIsHovered(false);
    };

    // Smoothly interpolate the outer ring for a high-tech floating feel
    const renderLoop = () => {
      // Linear interpolation factor (smooth follow)
      ringX += (mouseX - ringX) * 0.18;
      ringY += (mouseY - ringY) * 0.18;

      if (ringRef.current) {
        ringRef.current.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
      }

      animId = requestAnimationFrame(renderLoop);
    };

    window.addEventListener("mousemove", onMouseMove, { passive: true });
    window.addEventListener("mousedown", onMouseDown, { passive: true });
    window.addEventListener("mouseup", onMouseUp, { passive: true });
    document.addEventListener("mouseenter", onMouseEnter);
    document.addEventListener("mouseleave", onMouseLeave);

    animId = requestAnimationFrame(renderLoop);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      document.removeEventListener("mouseenter", onMouseEnter);
      document.removeEventListener("mouseleave", onMouseLeave);
      cancelAnimationFrame(animId);
    };
  }, [visible]);

  if (isTouchDevice) return null;

  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 pointer-events-none z-[9999] transition-opacity duration-300 ${
        visible ? "opacity-100" : "opacity-0"
      }`}
    >
      {/* Outer Floating Reticle Ring */}
      <div
        ref={ringRef}
        className="fixed top-0 left-0 -ml-[16px] -mt-[16px] pointer-events-none will-change-transform"
      >
        <div
          className={`w-[32px] h-[32px] rounded-full border transition-all duration-200 ease-out flex items-center justify-center ${
            isHovered
              ? "scale-140 border-cyan bg-cyan/[0.08] shadow-[0_0_16px_rgba(79,216,255,0.45)] backdrop-blur-[0.5px]"
              : isClicking
              ? "scale-85 border-signal-400 bg-signal-400/[0.15] shadow-[0_0_12px_rgba(20,119,245,0.4)]"
              : "border-cyan/40 bg-white/[0.01] shadow-[0_0_8px_rgba(79,216,255,0.2)]"
          }`}
        >
          {/* Subtle crosshair tick marks for futuristic HUD look */}
          <span
            className={`absolute top-0 left-1/2 -translate-x-1/2 w-[3px] h-[1px] bg-cyan transition-opacity duration-200 ${
              isHovered ? "opacity-100" : "opacity-40"
            }`}
          />
          <span
            className={`absolute bottom-0 left-1/2 -translate-x-1/2 w-[3px] h-[1px] bg-cyan transition-opacity duration-200 ${
              isHovered ? "opacity-100" : "opacity-40"
            }`}
          />
          <span
            className={`absolute left-0 top-1/2 -translate-y-1/2 w-[1px] h-[3px] bg-cyan transition-opacity duration-200 ${
              isHovered ? "opacity-100" : "opacity-40"
            }`}
          />
          <span
            className={`absolute right-0 top-1/2 -translate-y-1/2 w-[1px] h-[3px] bg-cyan transition-opacity duration-200 ${
              isHovered ? "opacity-100" : "opacity-40"
            }`}
          />
        </div>
      </div>

      {/* Central Precise Point */}
      <div
        ref={dotRef}
        className="fixed top-0 left-0 -ml-[2.5px] -mt-[2.5px] pointer-events-none will-change-transform"
      >
        <div
          className={`w-[5px] h-[5px] rounded-full transition-transform duration-150 ${
            isHovered
              ? "scale-150 bg-cyan shadow-[0_0_10px_#4fd8ff]"
              : isClicking
              ? "scale-75 bg-signal-300 shadow-[0_0_6px_#6cb2ff]"
              : "bg-signal-400 shadow-[0_0_6px_rgba(79,216,255,0.8)]"
          }`}
        />
      </div>
    </div>
  );
}
