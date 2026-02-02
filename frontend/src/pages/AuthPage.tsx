import { useState } from 'react'
import { LoginForm } from '@/components/auth/LoginForm'
import { SignupForm } from '@/components/auth/SignupForm'

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)

  return (
    <div className="min-h-screen bg-gradient-subtle flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-1/2 -right-1/2 w-full h-full rounded-full opacity-30 blur-3xl"
          style={{
            background: 'radial-gradient(circle, oklch(0.7 0.1 260 / 30%) 0%, transparent 70%)',
          }}
        />
        <div
          className="absolute -bottom-1/2 -left-1/2 w-full h-full rounded-full opacity-20 blur-3xl"
          style={{
            background: 'radial-gradient(circle, oklch(0.6 0.12 280 / 25%) 0%, transparent 70%)',
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-md animate-scale-in">
        {isLogin ? (
          <LoginForm onSwitchToSignup={() => setIsLogin(false)} />
        ) : (
          <SignupForm onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </div>
    </div>
  )
}
