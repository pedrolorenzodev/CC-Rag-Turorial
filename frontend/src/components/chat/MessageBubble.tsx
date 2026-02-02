import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex animate-fade-up",
        isUser ? "justify-end" : "justify-start",
      )}
      style={{ animationDelay: "0ms", animationFillMode: "backwards" }}
    >
      <div
        className={cn(
          "rounded-4xl px-4 py-3 transition-[transform,box-shadow] duration-200",
          isUser
            ? "max-w-[80%] bg-[#e1e1e168] text-foreground rounded-br-md"
            : "w-full text-foreground rounded-bl-md",
        )}
      >
        <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed">
          {content}
        </p>
      </div>
    </div>
  );
}
