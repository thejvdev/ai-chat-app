"use client";

import { useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { ChatWindow } from "@/components/chat/chat-window";
import { useChatsStore } from "@/stores/chats.store";
import { useThreadStore } from "@/stores/thread.store";

export function HomeChatView() {
  const router = useRouter();

  const createTitle = useChatsStore((s) => s.createTitle);

  const activeChatId = useThreadStore((s) => s.activeChatId);
  const isStreaming = useThreadStore((s) => s.isStreaming);
  const clearThread = useThreadStore((s) => s.clearThread);
  const cancelStream = useThreadStore((s) => s.cancelStream);
  const sendMessage = useThreadStore((s) => s.sendMessage);

  const startedHere = useRef(false);

  useEffect(() => {
    startedHere.current = false;
    clearThread();
  }, [clearThread]);

  useEffect(() => {
    if (!startedHere.current) return;
    if (!isStreaming) return;
    if (!activeChatId) return;

    router.replace(`/chats/${activeChatId}`);
  }, [activeChatId, isStreaming, router]);

  const handleSend = useCallback(
    async (query: string) => {
      startedHere.current = true;
      const chatId = await sendMessage(null, query);
      if (chatId) void createTitle(chatId, query);
    },
    [sendMessage, createTitle]
  );

  return (
    <ChatWindow
      isStreaming={isStreaming}
      onCancel={cancelStream}
      onSend={handleSend}
    >
      <span className="flex-1 flex justify-center items-center font-semibold text-2xl">
        How can I help you today?
      </span>
    </ChatWindow>
  );
}
