export type Role = "user" | "assistant";

export type Chat = {
  id: string;
  title: string;
};

export type ChatMessage = {
  id: string;
  role: Role;
  content: string;
};
