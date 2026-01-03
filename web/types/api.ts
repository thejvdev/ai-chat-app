export type ApiUserDto = {
  id: string;
  full_name: string;
  email: string;
};

export type ApiChatTitleDto = {
  title: string;
};

export type ApiChatDto = {
  id: string;
  title: string;
};

export type ApiMessageDto = {
  role: "user" | "assistant";
  content: string;
};

export type ApiChatsListDto = { chats: ApiChatDto[] };
export type ApiMessagesListDto = { messages: ApiMessageDto[] };

export type ApiError = {
  status: number;
  data: { detail?: string };
};

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === "object" && err !== null && "status" in err && "data" in err
  );
}

export type SseEvent = {
  event: string;
  data: string;
};
