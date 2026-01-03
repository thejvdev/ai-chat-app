import { useChatsStore } from "@/stores/chats.store";
import { useThreadStore } from "@/stores/thread.store";

export async function removeChat(chatId: string) {
  const thread = useThreadStore.getState();
  if (thread.activeChatId === chatId) thread.clearThread();

  await useChatsStore.getState().removeChat(chatId);
}

export async function clearChats() {
  useThreadStore.getState().clearThread();
  await useChatsStore.getState().clearChats();
}
