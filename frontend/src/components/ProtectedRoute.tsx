'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
  fallbackPath?: string
}

export default function ProtectedRoute({ 
  children, 
  fallbackPath = '/login' 
}: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      // Store the current path to redirect back after login
      const currentPath = window.location.pathname
      const redirectParam = currentPath !== '/' ? `?redirect=${encodeURIComponent(currentPath)}` : ''
      router.push(`${fallbackPath}${redirectParam}`)
    }
  }, [user, loading, router, fallbackPath])

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  // Show nothing while redirecting
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Redirecting to login...</div>
      </div>
    )
  }

  // User is authenticated, show the protected content
  return <>{children}</>
}