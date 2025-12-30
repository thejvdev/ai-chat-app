import ReactMarkdown from "react-markdown";
import RemarkGfm from "remark-gfm";
import type { ChatMessage } from "@/types/chat";

export function MessageLayout({ role, content }: ChatMessage) {
  if (role === "user") {
    return (
      <div className="w-full flex justify-end">
        <div className="max-w-[calc(100%-2rem)] rounded-lg bg-muted px-2.5 py-1.5 whitespace-pre-wrap">
          {content}
        </div>
      </div>
    );
  }

  return <ReactMarkdown remarkPlugins={[RemarkGfm]}>{content}</ReactMarkdown>;
}
