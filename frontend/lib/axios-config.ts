/**
 * Axios 全局配置
 * 处理请求拦截和响应拦截
 */
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18890',
  timeout: 90000, // 90秒超时
})

// 请求拦截器：自动添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理 401 错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 如果是 401 错误，清除本地认证信息
    if (error.response?.status === 401) {
      console.warn('Token 无效或已过期，清除本地认证信息')
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      
      // 可选：重定向到登录页
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
