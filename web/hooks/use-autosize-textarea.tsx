import * as React from "react";

export function useAutosizeTextarea(
  ref: React.RefObject<HTMLTextAreaElement | null>,
  value: string,
  { minPx = 64, maxPx = 160 }: { minPx?: number; maxPx?: number } = {}
) {
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;

    el.style.height = "auto";
    const next = Math.max(minPx, Math.min(el.scrollHeight, maxPx));
    el.style.height = `${next}px`;
    el.style.overflowY = el.scrollHeight > maxPx ? "auto" : "hidden";
  }, [ref, value, minPx, maxPx]);
}
