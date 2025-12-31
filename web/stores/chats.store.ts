import { create } from "zustand";
import type { Chat } from "@/types/chat";
import { GET, POST, DELETE } from "@/lib/api";
import type { ApiChatDto, ApiChatsListDto } from "@/types/api";
import { useThreadStore } from "@/stores/thread.store";

const getActiveChatId = () => useThreadStore.getState().activeChatId;
const resetActiveChat = () => useThreadStore.getState().clearThread();

interface ChatsState {
  chats: Chat[];

  loadChats: () => Promise<void>;
  createChat: (query: string) => Promise<string | null>;

  removeChat: (chatId: string) => Promise<void>;
  clearChats: () => Promise<void>;
}

export const useChatsStore = create<ChatsState>((set, get) => ({
  chats: [],

  loadChats: async () => {
    const data = await GET<ApiChatsListDto>("/chats");
    set({
      chats: (data.chats ?? []).map((c) => ({ id: c.id, title: c.title })),
    });
  },

  createChat: async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return null;

    const newChat = await POST<ApiChatDto, { query: string }>("/chats", {
      query: trimmed,
    });

    set((state) => ({
      chats: [{ id: newChat.id, title: newChat.title }, ...state.chats],
    }));

    return newChat.id;
  },

  removeChat: async (chatId: string) => {
    const prevChats = get().chats;

    if (getActiveChatId() === chatId) resetActiveChat();

    set((state) => ({ chats: state.chats.filter((c) => c.id !== chatId) }));

    try {
      await DELETE(`/chats/${chatId}`);
    } catch (e) {
      set({ chats: prevChats });
      throw e;
    }
  },

  clearChats: async () => {
    const prevChats = get().chats;
    if (prevChats.length <= 0) return;

    resetActiveChat();
    set({ chats: [] });

    try {
      await DELETE("/chats");
    } catch (e) {
      set({ chats: prevChats });
      throw e;
    }
  },
}));
