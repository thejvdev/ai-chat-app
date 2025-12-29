import { create } from "zustand";
import type { Message } from "@/types/chat";
import { GET } from "@/lib/api";

interface ThreadState {
  messages: Message[];
  isStreaming: boolean;

  loadMessages: () => Promise<void>;
  sendMessage: (query: string) => Promise<void>;
}

type MessagesState = {
  messages: Message[];
};

const getChatIdFromUrl = (): string | null => {
  if (typeof window === "undefined") return null;
  const match = window.location.pathname.match(/\/chats\/([^/]+)/);
  return match?.[1] ?? null;
};

export const useThreadStore = create<ThreadState>((set) => ({
  messages: [],
  isStreaming: false,

  loadMessages: async () => {
    const chatId = getChatIdFromUrl();
    if (!chatId) return;

    const data = (await GET(
      `/chats/${chatId}/messages`
    )) as MessagesState | null;
    set({ messages: data?.messages ?? [] });
  },

  sendMessage: async (query: string) => {
    query = query.trim();
    if (query.length <= 1) return;

    const chatId = getChatIdFromUrl();
    if (!chatId) return;

    set((state) => ({
      messages: [
        ...state.messages,
        { role: "user", content: query },
        { role: "assistant", content: "" },
      ],
      isStreaming: true,
    }));

    try {
      const res = await fetch(`/chats/${chatId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        credentials: "include",
        body: JSON.stringify({ query }),
      });

      if (!res.ok || !res.body) {
        set({ isStreaming: false });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        let idx = buffer.indexOf("\n\n");
        while (idx !== -1) {
          const block = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);

          if (block.split("\n").some((l) => l.trim() === "event: done")) {
            set({ isStreaming: false });
            return;
          }

          const data = block
            .split("\n")
            .filter((l) => l.startsWith("data:"))
            .map((l) => (l.startsWith("data: ") ? l.slice(6) : l.slice(5)))
            .join("\n");

          if (data) {
            set((state) => {
              const messages = state.messages.slice();

              for (let i = messages.length - 1; i >= 0; i--) {
                if (messages[i].role === "assistant") {
                  messages[i] = {
                    ...messages[i],
                    content: messages[i].content + data,
                  };
                  break;
                }
              }

              return { messages };
            });
          }

          idx = buffer.indexOf("\n\n");
        }
      }
    } finally {
      set({ isStreaming: false });
    }
  },
}));
