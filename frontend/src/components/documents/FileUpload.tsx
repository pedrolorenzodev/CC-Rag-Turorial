import { useCallback, useState } from 'react'
import { Button } from '@/components/ui/button'

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
  uploading: boolean
  accept?: string
}

export function FileUpload({ onUpload, uploading, accept = '.txt,.md,.pdf,.json,.csv' }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(
    async (file: File) => {
      setError(null)
      try {
        await onUpload(file)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed')
      }
    },
    [onUpload]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
      // Reset input so same file can be selected again
      e.target.value = ''
    },
    [handleFile]
  )

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50'
        } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-muted-foreground"
              aria-hidden="true"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-medium">
              {uploading ? 'Uploading...' : 'Drag and drop a file here'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Supported: TXT, MD, PDF, JSON, CSV (max 10MB)
            </p>
          </div>
          <label>
            <Button variant="outline" size="sm" disabled={uploading} asChild>
              <span>
                <input
                  type="file"
                  className="sr-only"
                  accept={accept}
                  onChange={handleFileInput}
                  disabled={uploading}
                />
                Browse files
              </span>
            </Button>
          </label>
        </div>
      </div>
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </div>
  )
}
