import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) {
    throw new Error('Not authenticated')
  }
  return {
    'Authorization': `Bearer ${session.access_token}`,
    'Content-Type': 'application/json',
  }
}

export interface Thread {
  id: string
  user_id: string
  title: string | null
  openai_thread_id: string | null
  vector_store_id: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  thread_id: string
  user_id: string
  role: 'user' | 'assistant'
  content: string
  metadata: Record<string, unknown>
  created_at: string
}

export const api = {
  async listThreads(): Promise<Thread[]> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads`, { headers })
    if (!response.ok) throw new Error('Failed to fetch threads')
    return response.json()
  },

  async createThread(title?: string): Promise<Thread> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ title }),
    })
    if (!response.ok) throw new Error('Failed to create thread')
    return response.json()
  },

  async getThread(threadId: string): Promise<Thread> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads/${threadId}`, { headers })
    if (!response.ok) throw new Error('Failed to fetch thread')
    return response.json()
  },

  async deleteThread(threadId: string): Promise<void> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads/${threadId}`, {
      method: 'DELETE',
      headers,
    })
    if (!response.ok) throw new Error('Failed to delete thread')
  },

  async getMessages(threadId: string): Promise<Message[]> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads/${threadId}/messages`, { headers })
    if (!response.ok) throw new Error('Failed to fetch messages')
    return response.json()
  },

  async sendMessage(threadId: string, content: string): Promise<ReadableStreamDefaultReader<Uint8Array>> {
    const headers = await getAuthHeaders()
    const response = await fetch(`${API_URL}/api/threads/${threadId}/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content }),
    })
    if (!response.ok) throw new Error('Failed to send message')
    if (!response.body) throw new Error('No response body')
    return response.body.getReader()
  },
}
