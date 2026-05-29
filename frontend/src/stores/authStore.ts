import { create } from 'zustand'
import type { UserProfile } from '../types/user'

interface AuthState {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  login: (user: UserProfile, token: string) => void
  logout: () => void
  setUser: (user: UserProfile) => void
}

export const useAuthStore = create<AuthState>((set) => {
  const storedToken = localStorage.getItem('access_token')
  const storedUser = localStorage.getItem('user')
  let initialUser: UserProfile | null = null
  try {
    if (storedUser) initialUser = JSON.parse(storedUser)
  } catch {
    localStorage.removeItem('user')
  }

  return {
    user: initialUser,
    token: storedToken,
    isAuthenticated: !!storedToken && !!initialUser,
    login: (user, token) => {
      localStorage.setItem('access_token', token)
      localStorage.setItem('user', JSON.stringify(user))
      set({ user, token, isAuthenticated: true })
    },
    logout: () => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, token: null, isAuthenticated: false })
    },
    setUser: (user) => {
      localStorage.setItem('user', JSON.stringify(user))
      set({ user })
    },
  }
})
