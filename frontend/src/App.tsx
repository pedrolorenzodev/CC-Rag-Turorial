import { useState } from 'react'
import { AuthProvider } from '@/contexts/AuthContext'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { ChatPage } from '@/pages/ChatPage'
import { DocumentsPage } from '@/pages/DocumentsPage'
import { AppLayout } from '@/layouts/AppLayout'

type Page = 'chat' | 'documents'

function AppContent() {
  const [currentPage, setCurrentPage] = useState<Page>('chat')

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === 'chat' && <ChatPage />}
      {currentPage === 'documents' && <DocumentsPage />}
    </AppLayout>
  )
}

function App() {
  return (
    <AuthProvider>
      <AuthGuard>
        <AppContent />
      </AuthGuard>
    </AuthProvider>
  )
}

export default App
