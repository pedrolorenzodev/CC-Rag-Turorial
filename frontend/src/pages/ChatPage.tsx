import { useState, useCallback } from 'react'
import { MainLayout } from '@/layouts/MainLayout'
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

  const sidebar = (
    <ThreadList
      threads={threads}
      activeThreadId={activeThreadId}
      onSelectThread={setActiveThreadId}
      onDeleteThread={handleDeleteThread}
      onNewThread={handleNewThread}
      loading={loading}
    />
  )

  return (
    <MainLayout sidebar={sidebar}>
      <ChatContainer threadId={activeThreadId} />
    </MainLayout>
  )
}
