'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, User } from '@/lib/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const isAuthenticated = !!user && apiClient.isAuthenticated()
  
  // Debug logging
  console.log('AuthProvider state - user:', !!user, 'token:', apiClient.isAuthenticated(), 'isAuthenticated:', isAuthenticated)

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      console.log('🔄 Initializing auth...')
      
      // Check if we have a stored user and token
      const storedUser = apiClient.getCurrentUserFromStorage()
      const hasToken = apiClient.isAuthenticated()
      
      console.log('📦 Stored user:', storedUser)
      console.log('🎫 Has token:', hasToken)
      
      if (storedUser && hasToken) {
        console.log('✅ Found stored user and token, setting user state...')
        setUser(storedUser)
        
        // Optional: Verify the token is still valid by fetching current user
        // For now, just trust the stored user to avoid API calls on every page load
        /*
        try {
          const currentUser = await apiClient.getCurrentUser()
          setUser(currentUser)
        } catch (error) {
          // Token might be expired, try to refresh
          try {
            await apiClient.refreshToken()
            const currentUser = await apiClient.getCurrentUser()
            setUser(currentUser)
          } catch (refreshError) {
            // Refresh failed, clear auth
            await apiClient.logout()
            setUser(null)
          }
        }
        */
      } else {
        console.log('❌ No stored user or token found')
        setUser(null)
      }
    } catch (error) {
      console.error('Auth initialization error:', error)
      await apiClient.logout()
      setUser(null)
    } finally {
      setIsLoading(false)
      console.log('🏁 Auth initialization complete')
    }
  }

  const login = async (email: string, password: string) => {
    try {
      console.log('Starting login...')
      const response = await apiClient.login({ email, password })
      console.log('API login response:', response)
      
      setUser(response.user)
      console.log('User state set to:', response.user)
      console.log('Token stored:', apiClient.isAuthenticated())
      console.log('User from localStorage:', apiClient.getCurrentUserFromStorage())
      
      // Force a re-render to check state
      setTimeout(() => {
        console.log('After timeout - user state:', user)
        console.log('After timeout - isAuthenticated:', !!user && apiClient.isAuthenticated())
      }, 100)
      
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const register = async (email: string, password: string, name: string) => {
    try {
      await apiClient.register({ email, password, name })
      // Auto-login after registration
      await login(email, password)
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await apiClient.logout()
      setUser(null)
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
      // Force logout even if API call fails
      setUser(null)
      router.push('/login')
    }
  }

  const refreshUser = async () => {
    try {
      if (apiClient.isAuthenticated()) {
        const currentUser = await apiClient.getCurrentUser()
        setUser(currentUser)
      }
    } catch (error) {
      console.error('Refresh user error:', error)
      // If refresh fails, try to refresh token
      try {
        await apiClient.refreshToken()
        const currentUser = await apiClient.getCurrentUser()
        setUser(currentUser)
      } catch (refreshError) {
        // If all fails, logout
        await logout()
      }
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Higher-order component for protected routes
export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login')
      }
    }, [isAuthenticated, isLoading, router])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null
    }

    return <Component {...props} />
  }
}

// Hook for role-based access
export function useRole() {
  const { user } = useAuth()
  
  return {
    role: user?.role || null,
    isSuperAdmin: user?.role === 'superadmin',
    isAdmin: user?.role === 'admin' || user?.role === 'superadmin',
    isManager: user?.role === 'manager',
    isEmployee: user?.role === 'employee' || user?.role === 'worker',
    
    // User Management Permissions
    canManageUsers: user?.role === 'admin' || user?.role === 'superadmin',
    canCreateUsers: user?.role === 'admin' || user?.role === 'superadmin',
    canDeleteUsers: user?.role === 'superadmin',
    
    // Inventory Permissions  
    canViewAllInventory: user?.role === 'admin' || user?.role === 'superadmin' || user?.role === 'manager',
    canViewUserInventory: user?.role === 'admin' || user?.role === 'superadmin',
    canManageOwnInventory: true, // All users can manage their own inventory
    
    // Safety Permissions
    canApproveChecklists: user?.role === 'admin' || user?.role === 'superadmin' || user?.role === 'manager',
    canViewAllChecklists: user?.role === 'admin' || user?.role === 'superadmin' || user?.role === 'manager',
    
    // General Permissions
    canViewReports: user?.role === 'admin' || user?.role === 'superadmin' || user?.role === 'manager',
    canManageSettings: user?.role === 'admin' || user?.role === 'superadmin'
  }
}
