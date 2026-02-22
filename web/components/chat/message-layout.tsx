import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import rehypeSanitize from "rehype-sanitize";
import rehypeExternalLinks from "rehype-external-links";
import type { ChatMessage } from "@/types/chat";

function normalizeLLM(input: string) {
  if (!input) return input;

  let s = input;

  s = s.replace(/([.!?:;])(\s*)(\d+)\.\s+/g, "$1\n\n$3. ");
  s = s.replace(/([.!?:;])(\s*)([-*])\s+/g, "$1\n\n$3 ");

  s = s.replace(/:\s*(ts|tsx|js|jsx)\s*\/\//g, ":\n\n$1//");
  s = s.replace(/([^\n])\s*(ts|tsx|js|jsx)\s*\/\//g, "$1\n\n$2//");

  s = s.replace(
    /([^\n])\s+(In your|By following|Remember|Overall)\b/g,
    "$1\n\n$2"
  );

  const startRe = /(?:^|\n\n)(ts|tsx|js|jsx)\s*\/\/ ?/g;

  let out = "";
  let last = 0;
  let m: RegExpExecArray | null;

  while ((m = startRe.exec(s))) {
    const lang = m[1];
    const start = m.index + (m[0].startsWith("\n\n") ? 2 : 0);

    out += s.slice(last, start);

    const codeStart = start + lang.length + 2;

    const nextBreak = s.indexOf("\n\n", codeStart);
    const codeEnd = nextBreak === -1 ? s.length : nextBreak;

    let code = s.slice(codeStart, codeEnd);

    code = code
      .replace(/\s*;\s*/g, ";\n")
      .replace(/\s*}\s*/g, "}\n")
      .replace(/\s*{\s*/g, " {\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();

    out += `\n\`\`\`${lang}\n//${code}\n\`\`\`\n`;

    last = codeEnd;
    startRe.lastIndex = codeEnd;
  }

  out += s.slice(last);

  out = out.replace(/\n{3,}/g, "\n\n");

  return out;
}

const components: Components = {
  pre: ({ children, ...props }) => (
    <pre
      className="my-3 overflow-x-auto rounded-lg bg-muted p-3 font-mono text-sm"
      {...props}
    >
      {children}
    </pre>
  ),
  code: ({ className, children, ...props }) => (
    <code
      className={
        className
          ? `${className} font-mono text-sm`
          : "rounded bg-muted px-1.5 py-0.5 font-mono text-sm"
      }
      {...props}
    >
      {children}
    </code>
  ),
  ol: ({ children, ...props }) => (
    <ol className="my-2 ml-5 list-decimal" {...props}>
      {children}
    </ol>
  ),
  ul: ({ children, ...props }) => (
    <ul className="my-2 ml-5 list-disc" {...props}>
      {children}
    </ul>
  ),
  li: ({ children, ...props }) => (
    <li className="my-1" {...props}>
      {children}
    </li>
  ),
  p: ({ children, ...props }) => (
    <p className="my-2 leading-relaxed" {...props}>
      {children}
    </p>
  ),
  a: ({ children, ...props }) => (
    <a className="underline underline-offset-4" {...props}>
      {children}
    </a>
  ),
};

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

  const normalized = normalizeLLM(content);

  return (
    <div className="max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        rehypePlugins={[
          rehypeSanitize,
          [
            rehypeExternalLinks,
            { target: "_blank", rel: ["noopener", "noreferrer"] },
          ],
        ]}
        skipHtml
        components={components}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  );
}
