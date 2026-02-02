import { type ReactNode } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { AuthPage } from '@/pages/AuthPage'

interface AuthGuardProps {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return <>{children}</>
}
