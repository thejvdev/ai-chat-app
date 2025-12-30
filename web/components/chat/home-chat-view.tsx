"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";

import { ChatWindow } from "@/components/chat/chat-window";
import { useChatsStore } from "@/stores/chats.store";
import { useThreadStore } from "@/stores/thread.store";

export function HomeChatView() {
  const router = useRouter();

  const createChat = useChatsStore((s) => s.createChat);
  const setPending = useThreadStore((s) => s.setPending);
  const clearThread = useThreadStore((s) => s.clearThread);

  useEffect(() => {
    clearThread();
  }, [clearThread]);

  const handleSend = useCallback(
    async (query: string) => {
      const text = query.trim();
      if (!text) return;

      const id = await createChat(text);
      if (!id) return;

      setPending(id, text);
      router.replace(`/chats/${id}`);
    },
    [createChat, setPending, router]
  );

  return <ChatWindow messages={[]} onSend={handleSend} />;
}
