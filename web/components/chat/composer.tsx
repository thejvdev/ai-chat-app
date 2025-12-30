import * as React from "react";
import { Textarea } from "@/components/ui/textarea";
import { useAutosizeTextarea } from "@/hooks/use-autosize-textarea";

export function Composer({
  value,
  onChange,
  onSend,
  minPx = 72,
  maxPx = 160,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => Promise<void>;
  minPx?: number;
  maxPx?: number;
}) {
  const ref = React.useRef<HTMLTextAreaElement | null>(null);
  useAutosizeTextarea(ref, value, { minPx, maxPx });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void onSend();
      }}
      className="shrink-0 py-4"
    >
      <Textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            void onSend();
          }
        }}
        placeholder="Message..."
        className="rounded-xl p-3 resize-none !text-base"
        style={{ minHeight: minPx, maxHeight: maxPx }}
      />
    </form>
  );
}
