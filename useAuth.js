import { useState, useEffect, createContext, useContext } from 'react'
import apiService from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      setIsLoading(true)
      const response = await apiService.getAuthStatus()
      
      if (response.authenticated) {
        setUser(response.employee)
      } else {
        setUser(null)
      }
    } catch (error) {
      console.error('Auth status check failed:', error)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (credentials) => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await apiService.login(credentials)
      
      if (response.success) {
        setUser(response.employee)
        return { success: true }
      } else {
        throw new Error('Login failed')
      }
    } catch (error) {
      const errorMessage = error.message || 'Login failed. Please check your credentials.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      setIsLoading(true)
      await apiService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setError(null)
      setIsLoading(false)
    }
  }

  const clearError = () => {
    setError(null)
  }

  const value = {
    user,
    isLoading,
    error,
    login,
    logout,
    clearError,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

