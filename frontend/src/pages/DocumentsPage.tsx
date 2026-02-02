import { useDocuments } from '@/hooks/useDocuments'
import { FileUpload } from '@/components/documents/FileUpload'
import { DocumentList } from '@/components/documents/DocumentList'

export function DocumentsPage() {
  const {
    documents,
    loading,
    error,
    uploading,
    uploadDocument,
    deleteDocument,
    processDocument,
  } = useDocuments()

  const handleUpload = async (file: File) => {
    const doc = await uploadDocument(file)
    // Auto-process after upload
    await processDocument(doc.id)
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b p-4">
        <h1 className="text-xl font-semibold">Documents</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Upload and manage documents for RAG retrieval
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto space-y-8">
          <FileUpload onUpload={handleUpload} uploading={uploading} />

          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <div>
            <h2 className="text-lg font-medium mb-4">Your Documents</h2>
            <DocumentList
              documents={documents}
              loading={loading}
              onDelete={deleteDocument}
              onProcess={processDocument}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
