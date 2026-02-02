import { type Thread } from '@/lib/api'
import { ThreadItem } from './ThreadItem'
import { Button } from '@/components/ui/button'

interface ThreadListProps {
  threads: Thread[]
  activeThreadId: string | null
  onSelectThread: (threadId: string) => void
  onDeleteThread: (threadId: string) => void
  onNewThread: () => void
  loading: boolean
}

export function ThreadList({
  threads,
  activeThreadId,
  onSelectThread,
  onDeleteThread,
  onNewThread,
  loading,
}: ThreadListProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4">
        <Button
          onClick={onNewThread}
          className="w-full group"
        >
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
            className="mr-2 transition-transform duration-200 group-hover:rotate-90"
            aria-hidden="true"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
          New Chat
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {loading ? (
          <div className="space-y-2 px-1">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="h-16 rounded-xl shimmer"
                style={{ animationDelay: `${i * 100}ms` }}
              />
            ))}
          </div>
        ) : threads.length === 0 ? (
          <div className="p-6 text-center animate-fade-in">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-accent flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-muted-foreground"
                aria-hidden="true"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">No conversations yet</p>
            <p className="text-xs text-muted-foreground/70 mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {threads.map((thread, index) => (
              <div
                key={thread.id}
                className="animate-slide-in-right"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <ThreadItem
                  thread={thread}
                  isActive={thread.id === activeThreadId}
                  onSelect={() => onSelectThread(thread.id)}
                  onDelete={() => onDeleteThread(thread.id)}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
