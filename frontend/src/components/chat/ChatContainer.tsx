import { useEffect } from 'react'
import { useChat } from '@/hooks/useChat'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'

interface ChatContainerProps {
  threadId: string | null
}

export function ChatContainer({ threadId }: ChatContainerProps) {
  const { messages, streamingContent, isLoadingMessages, isSending, error, loadMessages, sendMessage } =
    useChat(threadId)

  useEffect(() => {
    loadMessages()
  }, [loadMessages])

  if (!threadId) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 bg-gradient-subtle">
        <div className="text-center animate-fade-up max-w-md">
          <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-accent flex items-center justify-center shadow-lg">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-muted-foreground"
              aria-hidden="true"
            >
              {/* Head */}
              <rect x="5" y="2" width="14" height="12" rx="3" />
              {/* Eyes */}
              <circle cx="9" cy="8" r="1.5" fill="currentColor" />
              <circle cx="15" cy="8" r="1.5" fill="currentColor" />
              {/* Antenna */}
              <path d="M12 2V0" />
              <circle cx="12" cy="0" r="1" fill="currentColor" />
              {/* Mouth/speaker */}
              <path d="M9 11h6" />
              {/* Neck */}
              <path d="M10 14v2h4v-2" />
              {/* Body */}
              <rect x="6" y="16" width="12" height="6" rx="2" />
              {/* Arms */}
              <path d="M6 18H4a1 1 0 0 0-1 1v2" />
              <path d="M18 18h2a1 1 0 0 1 1 1v2" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">No chat selected</h2>
          <p className="text-muted-foreground leading-relaxed">
            Select a conversation from the sidebar or create a new one to get started.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gradient-subtle">
      {error && (
        <div className="px-6 py-3 bg-destructive/10 border-b border-destructive/20 animate-fade-in">
          <div className="flex items-center gap-2 text-destructive text-sm">
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
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        </div>
      )}
      <MessageList
        messages={messages}
        streamingContent={streamingContent}
        isLoadingMessages={isLoadingMessages}
        isSending={isSending}
      />
      <ChatInput onSend={sendMessage} disabled={isSending} />
    </div>
  )
}
