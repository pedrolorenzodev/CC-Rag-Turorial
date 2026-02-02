import { useState, useCallback } from 'react'
import { ThreadList } from '@/components/chat/ThreadList'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { useThreads } from '@/hooks/useThreads'

export function ChatPage() {
  const { threads, loading, createThread, deleteThread } = useThreads()
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)

  const handleNewThread = useCallback(async () => {
    try {
      const newThread = await createThread()
      setActiveThreadId(newThread.id)
    } catch {
      // Error handled by useThreads
    }
  }, [createThread])

  const handleDeleteThread = useCallback(
    async (threadId: string) => {
      try {
        await deleteThread(threadId)
        if (activeThreadId === threadId) {
          setActiveThreadId(null)
        }
      } catch {
        // Error handled by useThreads
      }
    },
    [deleteThread, activeThreadId]
  )

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Thread sidebar */}
      <aside className="w-64 border-r bg-background/50 flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-semibold">Conversations</h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <ThreadList
            threads={threads}
            activeThreadId={activeThreadId}
            onSelectThread={setActiveThreadId}
            onDeleteThread={handleDeleteThread}
            onNewThread={handleNewThread}
            loading={loading}
          />
        </div>
      </aside>

      {/* Chat area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatContainer threadId={activeThreadId} />
      </div>
    </div>
  )
}
