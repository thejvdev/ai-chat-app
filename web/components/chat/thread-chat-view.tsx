"use client";

import { useEffect, useCallback } from "react";
import { useParams } from "next/navigation";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Spinner } from "@/components/ui/spinner";
import { MessageList } from "@/components/chat/message-list";
import { ChatWindow } from "@/components/chat/chat-window";
import { useThreadStore } from "@/stores/thread.store";

export function ThreadChatView() {
  const params = useParams<{ chatId: string }>();
  const chatId = params.chatId;

  const messages = useThreadStore((s) => s.messages);
  const activeChatId = useThreadStore((s) => s.activeChatId);
  const isStreaming = useThreadStore((s) => s.isStreaming);

  const loadMessages = useThreadStore((s) => s.loadMessages);
  const sendMessage = useThreadStore((s) => s.sendMessage);
  const cancelStream = useThreadStore((s) => s.cancelStream);
  const consumePending = useThreadStore((s) => s.consumePending);

  useEffect(() => {
    const first = consumePending(chatId);
    if (first) {
      void sendMessage(chatId, first);
      return;
    }

    if (activeChatId !== chatId) {
      loadMessages(chatId).catch(() => {});
    }
  }, [chatId, activeChatId, consumePending, sendMessage, loadMessages]);

  const handleSend = useCallback(
    async (query: string) => {
      await sendMessage(chatId, query);
    },
    [chatId, sendMessage]
  );

  const handleCancel = useCallback(() => cancelStream(), [cancelStream]);

  const last = messages[messages.length - 1];

  return (
    <ChatWindow
      isStreaming={isStreaming}
      onSend={handleSend}
      onCancel={handleCancel}
    >
      <ScrollArea className="flex-1 min-h-0 w-full">
        <div className="mx-auto w-full max-w-[768px] px-4 min-h-full flex flex-col">
          <MessageList messages={messages} />

          {isStreaming && last?.role === "assistant" && !last?.content && (
            <div className="flex items-center gap-1">
              <Spinner />
              Thinking
            </div>
          )}
        </div>
      </ScrollArea>
    </ChatWindow>
  );
}
