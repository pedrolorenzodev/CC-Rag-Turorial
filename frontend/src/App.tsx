import { AuthProvider } from '@/contexts/AuthContext'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { ChatPage } from '@/pages/ChatPage'

function App() {
  return (
    <AuthProvider>
      <AuthGuard>
        <ChatPage />
      </AuthGuard>
    </AuthProvider>
  )
}

export default App
