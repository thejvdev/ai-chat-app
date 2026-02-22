"use client";

import React, { useRef } from "react";
import { ArrowUp, Square } from "lucide-react";

import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useAutosizeTextarea } from "@/hooks/use-autosize-textarea";

interface ChatWindowProps {
  isStreaming: boolean;
  onSend: (query: string) => Promise<void>;
  onCancel: () => void;
  children: React.ReactNode;
}

const MIN_PX = 72;
const MAX_PX = 160;

export function ChatWindow({
  isStreaming,
  onSend,
  onCancel,
  children,
}: ChatWindowProps) {
  const [value, setValue] = React.useState("");
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useAutosizeTextarea(ref, value, { minPx: MIN_PX, maxPx: MAX_PX });

  const sendMessage = async () => {
    const text = value.trim();
    if (!text || isStreaming) return;

    setValue("");
    try {
      await onSend(text);
    } catch (error) {
      setValue(text);
      throw error;
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    void sendMessage();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  };

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden">
      {children}

      <div className="mx-auto w-full max-w-[768px] px-4">
        <form onSubmit={handleSubmit} className="shrink-0 py-4">
          <div className="relative">
            <Textarea
              ref={ref}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message..."
              className="rounded-xl p-3 pr-12 resize-none !text-base"
              style={{ minHeight: MIN_PX, maxHeight: MAX_PX }}
            />

            {!isStreaming ? (
              <Button
                type="submit"
                size="icon"
                className="absolute right-3 bottom-3 h-8 w-8 rounded-full"
                aria-label="Send message"
                title="Send"
              >
                <ArrowUp className="h-4 w-4" strokeWidth={2.5} />
              </Button>
            ) : (
              <Button
                type="button"
                size="icon"
                className="absolute right-3 bottom-3 h-8 w-8 rounded-full"
                aria-label="Stop generating"
                onClick={onCancel}
                title="Stop"
              >
                <Square className="h-4 w-4" fill="currentColor" />
              </Button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
