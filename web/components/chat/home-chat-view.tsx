"use client";

import { useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

import { ChatWindow } from "@/components/chat/chat-window";
import { useChatsStore } from "@/stores/chats.store";
import { useThreadStore } from "@/stores/thread.store";

export function HomeChatView() {
  const router = useRouter();

  const createChat = useChatsStore((s) => s.createChat);
  const setPending = useThreadStore((s) => s.setPending);
  const clearThread = useThreadStore((s) => s.clearThread);
  const cancelStream = useThreadStore((s) => s.cancelStream);

  useEffect(() => {
    clearThread();
  }, [clearThread]);

  // FIXME: Rewrite this logic - creation after streaming
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

  return (
    <ChatWindow isStreaming={false} onCancel={cancelStream} onSend={handleSend}>
      <span className="flex-1 flex justify-center items-center font-semibold text-2xl">
        How can I help you today?
      </span>
    </ChatWindow>
  );
}
