import type { ChatMessage } from "@/types/chat";
import { MessageLayout } from "@/components/chat/message-layout";

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  return (
    <div className="w-full py-4 space-y-4">
      {messages.map((m) => (
        <MessageLayout key={m.id} {...m} />
      ))}
    </div>
  );
}
