import React, { createContext, useContext, useEffect, useState } from 'react'
import { UserProfile, LoginResponse, ProfileResponse } from '@/models/banking.models'
import { apiService } from '@/services/api.service'

interface AuthContextType {
  currentUser: UserProfile | null
  isAuthenticated: boolean
  isLoading: boolean
  register: (payload: {
    username: string
    email: string
    password: string
    password2: string
    first_name: string
    last_name: string
    phone_number: string
  }) => Promise<ProfileResponse>
  login: (usernameOrEmail: string, password: string) => Promise<LoginResponse>
  logout: () => void
  fetchProfile: () => Promise<void>
  updateProfile: (payload: Record<string, string>) => Promise<ProfileResponse>
  changePassword: (payload: {
    old_password: string
    new_password: string
    new_password2: string
  }) => Promise<{ success: boolean; message: string }>
  setSession: (access: string, refresh: string, user: UserProfile) => void
  verifyEmail: (token: string) => Promise<{ success: boolean; message: string }>
  forgotPassword: (email: string) => Promise<{ success: boolean; message: string }>
  resetPassword: (token: string, newPassword: string, newPassword2: string) => Promise<{ success: boolean; message: string }>
  requestOTP: (email: string) => Promise<{ success: boolean; message: string }>
  verifyOTP: (email: string, otp: string) => Promise<LoginResponse>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const accessTokenKey = 'net-bank-access-token'
const refreshTokenKey = 'net-bank-refresh-token'
const userKey = 'net-bank-user'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Restore session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem(userKey)
    if (storedUser) {
      try {
        setCurrentUser(JSON.parse(storedUser))
      } catch {
        // Invalid stored user
        localStorage.removeItem(userKey)
      }
    }
    setIsLoading(false)
  }, [])

  const setSession = (access: string, refresh: string, user: UserProfile) => {
    localStorage.setItem(accessTokenKey, access)
    localStorage.setItem(refreshTokenKey, refresh)
    localStorage.setItem(userKey, JSON.stringify(user))
    setCurrentUser(user)
  }

  const clearSession = () => {
    localStorage.removeItem(accessTokenKey)
    localStorage.removeItem(refreshTokenKey)
    localStorage.removeItem(userKey)
    setCurrentUser(null)
  }

  const register = async (payload: {
    username: string
    email: string
    password: string
    password2: string
    first_name: string
    last_name: string
    phone_number: string
  }) => {
    return apiService.register(payload)
  }

  const login = async (usernameOrEmail: string, password: string) => {
    const response = await apiService.login({ username_or_email: usernameOrEmail, password })
    setSession(response.access, response.refresh, response.user)
    return response
  }

  const logout = () => {
    clearSession()
  }

  const fetchProfile = async () => {
    const response = await apiService.getProfile()
    setCurrentUser(response.user)
    localStorage.setItem(userKey, JSON.stringify(response.user))
  }

  const updateProfile = async (payload: Record<string, string>) => {
    const response = await apiService.updateProfile(payload)
    setCurrentUser(response.user)
    localStorage.setItem(userKey, JSON.stringify(response.user))
    return response
  }

  const changePassword = (payload: {
    old_password: string
    new_password: string
    new_password2: string
  }) => {
    return apiService.changePassword(payload)
  }

  const verifyEmail = (token: string) => {
    return apiService.verifyEmail({ token })
  }

  const forgotPassword = (email: string) => {
    return apiService.forgotPassword({ email, frontend_url: window.location.origin })
  }

  const resetPassword = (token: string, newPassword: string, newPassword2: string) => {
    return apiService.resetPassword({ token, new_password: newPassword, new_password2: newPassword2 })
  }

  const requestOTP = (email: string) => {
    return apiService.requestOTP({ email })
  }

  const verifyOTP = async (email: string, otp: string) => {
    const response = await apiService.verifyOTP({ email, otp })
    setSession(response.access, response.refresh, response.user)
    return response
  }

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        isLoading,
        register,
        login,
        logout,
        fetchProfile,
        updateProfile,
        changePassword,
        setSession,
        verifyEmail,
        forgotPassword,
        resetPassword,
        requestOTP,
        verifyOTP,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
