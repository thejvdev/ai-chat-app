import { create } from "zustand";
import type { ChatItem } from "@/types/chat";
import { GET, POST } from "@/lib/api";
import { ApiChat } from "@/types/api";

interface ChatsState {
  chats: ChatItem[];

  loadChats: () => Promise<void>;
  createChat: (query: string) => Promise<string | null>;
  removeChat: () => void;
  clearChats: () => void;
}

export const useChatsStore = create<ChatsState>((set, get) => ({
  chats: [],

  loadChats: async () => {
    try {
      const chats = (await GET("/chats")) as ApiChat[];
      set({
        chats: chats.map((c) => ({ chatId: c.id, title: c.title })),
      });
    } catch {
      set({ chats: [] });
    }
  },

  createChat: async (query: string) => {
    const newChat = ((await POST("/chats", { query })) as ApiChat) || null;

    if (!newChat) return null;
    set({
      chats: [{ chatId: newChat.id, title: newChat.title }, ...get().chats],
    });

    return newChat.id;
  },

  removeChat: () => {},

  clearChats: () => {},
}));
