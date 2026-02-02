import { useState, useEffect, useCallback } from 'react'
import { api, type Thread } from '@/lib/api'

export function useThreads() {
  const [threads, setThreads] = useState<Thread[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchThreads = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.listThreads()
      setThreads(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch threads')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchThreads()
  }, [fetchThreads])

  const createThread = useCallback(async (title?: string) => {
    try {
      const newThread = await api.createThread(title)
      setThreads((prev) => [newThread, ...prev])
      return newThread
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create thread')
      throw err
    }
  }, [])

  const deleteThread = useCallback(async (threadId: string) => {
    try {
      await api.deleteThread(threadId)
      setThreads((prev) => prev.filter((t) => t.id !== threadId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete thread')
      throw err
    }
  }, [])

  return {
    threads,
    loading,
    error,
    createThread,
    deleteThread,
    refetch: fetchThreads,
  }
}
