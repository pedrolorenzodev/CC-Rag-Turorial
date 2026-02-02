import { useState, useCallback } from 'react'
import { api, type Message } from '@/lib/api'

export function useChat(threadId: string | null) {
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingContent, setStreamingContent] = useState<string | null>(null)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadMessages = useCallback(async () => {
    if (!threadId) {
      setMessages([])
      return
    }

    try {
      setIsLoadingMessages(true)
      setError(null)
      const data = await api.getMessages(threadId)
      setMessages(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages')
    } finally {
      setIsLoadingMessages(false)
    }
  }, [threadId])

  const sendMessage = useCallback(
    async (content: string) => {
      if (!threadId) return

      // Optimistically add user message
      const tempUserMessage: Message = {
        id: `temp-${Date.now()}`,
        thread_id: threadId,
        user_id: '',
        role: 'user',
        content,
        metadata: {},
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, tempUserMessage])
      setIsSending(true)
      setStreamingContent('')
      setError(null)

      try {
        const reader = await api.sendMessage(threadId, content)
        const decoder = new TextDecoder()
        let buffer = ''
        let fullResponse = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data:')) {
              // Handle both "data: content" and "data:content" formats
              let data = line.startsWith('data: ') ? line.slice(6) : line.slice(5)
              if (data !== '[DONE]') {
                // Decode escaped newlines and other escape sequences
                data = data.replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t')
                fullResponse += data
                setStreamingContent(fullResponse)
              }
            } else if (line.startsWith('event:')) {
              const event = line.slice(6).trim()
              if (event === 'done') {
                // Add the complete assistant message
                const assistantMessage: Message = {
                  id: `assistant-${Date.now()}`,
                  thread_id: threadId,
                  user_id: '',
                  role: 'assistant',
                  content: fullResponse,
                  metadata: {},
                  created_at: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, assistantMessage])
                setStreamingContent(null)
              } else if (event === 'error') {
                setError('An error occurred while generating the response')
              }
            }
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message')
        // Remove the optimistic user message on error
        setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id))
      } finally {
        setIsSending(false)
        setStreamingContent(null)
      }
    },
    [threadId]
  )

  return {
    messages,
    streamingContent,
    isLoadingMessages,
    isSending,
    error,
    loadMessages,
    sendMessage,
  }
}
