import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'
import type { Message } from '@/lib/api'

interface MessageListProps {
  messages: Message[]
  streamingContent: string | null
  isLoadingMessages: boolean
  isSending: boolean
}

export function MessageList({ messages, streamingContent, isLoadingMessages, isSending }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  // Loading messages from database
  if (isLoadingMessages) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="flex items-center gap-1">
            <span
              className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce-dot"
              style={{ animationDelay: '0ms' }}
            />
            <span
              className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce-dot"
              style={{ animationDelay: '150ms' }}
            />
            <span
              className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce-dot"
              style={{ animationDelay: '300ms' }}
            />
          </div>
        </div>
      </div>
    )
  }

  if (messages.length === 0 && !isSending) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <p className="text-2xl font-semibold text-muted-foreground">What can I help with?</p>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-[39rem] mx-auto space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            style={{ animationDelay: `${Math.min(index * 50, 300)}ms` }}
          >
            <MessageBubble role={message.role} content={message.content} />
          </div>
        ))}
        {streamingContent && (
          <MessageBubble role="assistant" content={streamingContent} />
        )}
        {isSending && !streamingContent && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
