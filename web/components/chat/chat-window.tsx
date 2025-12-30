"use client";

import * as React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage } from "@/types/chat";
import { MessageList } from "@/components/chat/message-list";
import { Composer } from "@/components/chat/composer";

export function ChatWindow({
  messages,
  onSend,
}: {
  messages: ChatMessage[];
  onSend: (query: string) => Promise<void>;
}) {
  const [value, setValue] = React.useState("");

  const handleSend = async () => {
    setValue("");
    await onSend(value);
  };

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden">
      {messages.length <= 0 ? (
        <span className="flex-1 flex justify-center items-center font-semibold text-xl">
          Type something to start
        </span>
      ) : (
        <ScrollArea className="flex-1 min-h-0 w-full">
          <div className="mx-auto w-full max-w-[768px] px-4 min-h-full flex">
            <MessageList messages={messages} />
          </div>
        </ScrollArea>
      )}

      <div className="mx-auto w-full max-w-[768px] px-4">
        <Composer value={value} onChange={setValue} onSend={handleSend} />
      </div>
    </div>
  );
}
