import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

const MAX_LINES = 5;
const LINE_HEIGHT = 20; // approximate line height in pixels for text-sm leading-relaxed

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = "auto";

    // Calculate max height based on max lines
    const maxHeight = LINE_HEIGHT * MAX_LINES;

    // Set height to scrollHeight, but cap at maxHeight
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
  }, [input]);

  const hasInput = input.trim().length > 0;

  return (
    <div className="bg-gradient-subtle p-4">
      <div className="flex items-end justify-center gap-2">
        <div
          className={cn(
            "flex items-center px-5 py-3 rounded-3xl border bg-background/80 backdrop-blur-sm transition-[border-color,box-shadow] duration-200 w-full max-w-xl",
            isFocused
              ? "border-ring/50 shadow-lg shadow-ring/10"
              : "border-border hover:border-border/80",
          )}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask anything"
            disabled={disabled}
            className="flex-1 resize-none bg-transparent text-sm leading-relaxed placeholder:text-muted-foreground/60 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed overflow-y-auto"
            rows={1}
          />
        </div>
        <button
          onClick={handleSend}
          disabled={!hasInput && !disabled}
          className={cn(
            "shrink-0 w-11 h-11 mb-[1px] rounded-full flex items-center justify-center transition-colors",
            disabled
              ? "bg-red-500 text-white cursor-pointer"
              : hasInput
                ? "bg-zinc-800 text-white hover:bg-zinc-900"
                : "bg-zinc-400 text-white cursor-not-allowed",
          )}
          aria-label={disabled ? "Stop generation" : "Send message"}
        >
          {disabled ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="4" y="4" width="16" height="16" rx="2" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z" />
              <path d="m21.854 2.147-10.94 10.939" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
