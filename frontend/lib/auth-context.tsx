"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

interface User {
  id: number
  email: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 从 localStorage 加载认证信息并验证
    const initializeAuth = async () => {
      const savedToken = localStorage.getItem('auth_token')
      const savedUser = localStorage.getItem('user')
      
      if (savedToken && savedUser) {
        try {
          // 验证 token 是否有效
          const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${savedToken}`
            }
          })
          
          // Token 有效，设置状态
          setToken(savedToken)
          setUser(response.data)
          
          // 更新 localStorage 中的用户信息（可能有更新）
          localStorage.setItem('user', JSON.stringify(response.data))
        } catch (error) {
          // Token 无效或过期，清除本地数据
          console.error('Token 验证失败:', error)
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user')
        }
      }
      
      setIsLoading(false)
    }
    
    initializeAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      setToken(access_token)
      setUser(userData)
      
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '登录失败')
    }
  }

  const register = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
        email,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      setToken(access_token)
      setUser(userData)
      
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '注册失败')
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
