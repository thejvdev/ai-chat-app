export type ChatItem = {
  chatId: string;
  title: string;
};

export type MessageRole = "user" | "assistant";

export type Message = {
  role: MessageRole;
  content: string;
};
