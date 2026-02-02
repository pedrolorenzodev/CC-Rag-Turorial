import { useState, useEffect, useCallback } from 'react'
import { api, type Document } from '@/lib/api'
import { supabase } from '@/lib/supabase'

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.listDocuments()
      setDocuments(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  // Subscribe to realtime updates for document status changes
  useEffect(() => {
    const channel = supabase
      .channel('documents-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'documents',
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setDocuments((prev) => [payload.new as Document, ...prev])
          } else if (payload.eventType === 'UPDATE') {
            setDocuments((prev) =>
              prev.map((doc) =>
                doc.id === payload.new.id ? (payload.new as Document) : doc
              )
            )
          } else if (payload.eventType === 'DELETE') {
            setDocuments((prev) =>
              prev.filter((doc) => doc.id !== payload.old.id)
            )
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const uploadDocument = useCallback(async (file: File) => {
    try {
      setUploading(true)
      setError(null)
      const newDoc = await api.uploadDocument(file)
      // Document will be added via realtime subscription, but add it optimistically
      setDocuments((prev) => {
        // Avoid duplicate if realtime already added it
        if (prev.some((d) => d.id === newDoc.id)) return prev
        return [newDoc, ...prev]
      })
      return newDoc
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to upload document'
      setError(message)
      throw err
    } finally {
      setUploading(false)
    }
  }, [])

  const deleteDocument = useCallback(async (documentId: string) => {
    try {
      await api.deleteDocument(documentId)
      setDocuments((prev) => prev.filter((d) => d.id !== documentId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document')
      throw err
    }
  }, [])

  const processDocument = useCallback(async (documentId: string) => {
    try {
      setError(null)
      // Optimistically update status
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId ? { ...doc, status: 'processing' as const } : doc
        )
      )
      await api.processDocument(documentId)
      // Refetch to get updated status (or rely on realtime)
      await fetchDocuments()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to process document'
      setError(message)
      // Refetch to get actual status
      await fetchDocuments()
      throw err
    }
  }, [fetchDocuments])

  return {
    documents,
    loading,
    error,
    uploading,
    uploadDocument,
    deleteDocument,
    processDocument,
    refetch: fetchDocuments,
  }
}
