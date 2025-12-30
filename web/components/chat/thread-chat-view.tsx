"use client";

import { useEffect, useCallback } from "react";
import { useParams } from "next/navigation";

import { ChatWindow } from "@/components/chat/chat-window";
import { useThreadStore } from "@/stores/thread.store";

export function ThreadChatView() {
  const params = useParams<{ chatId: string }>();
  const chatId = params.chatId;

  const messages = useThreadStore((s) => s.messages);
  const activeChatId = useThreadStore((s) => s.activeChatId);

  const loadMessages = useThreadStore((s) => s.loadMessages);
  const sendMessage = useThreadStore((s) => s.sendMessage);
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

  return <ChatWindow messages={messages} onSend={handleSend} />;
}
