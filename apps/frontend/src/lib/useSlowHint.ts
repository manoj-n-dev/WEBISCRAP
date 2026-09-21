import { useEffect, useState } from "react";

/** true once `active` has stayed true for `delayMs` — used to explain a cold start instead of an endless spinner. */
export function useSlowHint(active: boolean, delayMs = 4000): boolean {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!active) {
      setSlow(false);
      return;
    }
    const t = setTimeout(() => setSlow(true), delayMs);
    return () => clearTimeout(t);
  }, [active, delayMs]);
  return slow;
}
