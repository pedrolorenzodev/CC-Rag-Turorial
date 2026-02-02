import { type ReactNode } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'

interface MainLayoutProps {
  sidebar: ReactNode
  children: ReactNode
}

export function MainLayout({ sidebar, children }: MainLayoutProps) {
  const { user, signOut } = useAuth()

  return (
    <div className="flex h-screen bg-gradient-subtle">
      {/* Sidebar */}
      <aside className="w-72 border-r bg-gradient-sidebar flex flex-col shadow-xl shadow-black/5">
        <div className="p-5 border-b">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-primary flex items-center justify-center shadow-md shadow-black/10">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-primary-foreground"
                aria-hidden="true"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="font-semibold text-lg tracking-tight">RAG App</h1>
              <p className="text-xs text-muted-foreground">Intelligent Assistant</p>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-hidden">{sidebar}</div>
        <div className="p-4 border-t bg-background/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-accent flex items-center justify-center text-xs font-medium text-foreground/80 shrink-0">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.email}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={signOut}
              className="shrink-0 text-muted-foreground hover:text-foreground"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16,17 21,12 16,7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              <span className="sr-only">Sign out</span>
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
    </div>
  )
}
