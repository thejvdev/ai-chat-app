import { create } from "zustand";

import type { ApiMessagesListDto } from "@/types/api";
import type { ChatMessage } from "@/types/chat";
import { GET } from "@/lib/api";
import { POST_SSE } from "@/lib/sse";
import { withRefreshRetry, sseWithRefreshRetry } from "@/lib/retry";

import { useChatsStore } from "@/stores/chats.store";

const uid = () =>
  globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID()
    : `${Date.now()}-${Math.random()}`;

let currentAbort: AbortController | null = null;

interface ThreadState {
  activeChatId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;

  clearThread: () => void;
  cancelStream: () => void;

  loadMessages: (chatId: string) => Promise<void>;
  sendMessage: (chatId: string | null, query: string) => Promise<string | null>;
}

export const useThreadStore = create<ThreadState>((set, get) => ({
  activeChatId: null,
  messages: [],
  isStreaming: false,

  clearThread: () => {
    get().cancelStream();
    set({ activeChatId: null, messages: [], isStreaming: false });
  },

  cancelStream: () => {
    if (currentAbort) {
      currentAbort.abort();
      currentAbort = null;
    }
    set({ isStreaming: false });
  },

  loadMessages: async (chatId: string) => {
    if (get().isStreaming && get().activeChatId === chatId) return;

    if (get().activeChatId && get().activeChatId !== chatId) {
      get().cancelStream();
    }

    const data = (await withRefreshRetry(() =>
      GET(`/chats/${chatId}/messages`)
    )) as ApiMessagesListDto | null;

    set({
      activeChatId: chatId,
      isStreaming: false,
      messages: (data?.messages ?? []).map((m, i) => ({
        id: `${chatId}:${i}`,
        role: m.role,
        content: m.content,
      })),
    });
  },

  sendMessage: async (
    chatId: string | null,
    query: string
  ): Promise<string | null> => {
    const text = query.trim();
    if (!text) return null;

    get().cancelStream();

    const userId = uid();
    const assistantId = uid();

    set((s) => ({
      activeChatId: chatId,
      isStreaming: true,
      messages: [
        ...(s.activeChatId === chatId ? s.messages : []),
        { id: userId, role: "user", content: text },
        { id: assistantId, role: "assistant", content: "" },
      ],
    }));

    const abort = new AbortController();
    currentAbort = abort;

    try {
      const make = () =>
        POST_SSE(
          "/chats/stream",
          { query: text, chat_id: chatId },
          abort.signal
        );

      for await (const event of sseWithRefreshRetry(make)) {
        if (event.event === "meta") {
          const meta = JSON.parse(event.data) as { chat_id: string };
          chatId = meta.chat_id;

          useChatsStore.getState().addChat(chatId);
          set({ activeChatId: chatId });
          continue;
        }

        if (event.event === "stream") {
          const payload = JSON.parse(event.data) as { text: string };
          const chunk = payload.text ?? "";
          if (!chunk) continue;

          set((s) => ({
            messages: s.messages.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + chunk } : m
            ),
          }));
          continue;
        }

        if (event.event === "error") {
          break;
        }

        if (event.event === "done") break;
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return chatId;
      throw e;
    } finally {
      if (currentAbort === abort) {
        currentAbort = null;
        set({ isStreaming: false });
      }
    }

    return chatId;
  },
}));
