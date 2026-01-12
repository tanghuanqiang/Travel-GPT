/**
 * API工具函数
 * 封装所有API调用
 */
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18890'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface ShareLinkResponse {
  share_token: string
  share_url: string
  is_public: boolean
  expires_at: string | null
}

export const api = {
  // 分享相关
  createShareLink: async (itineraryId: number, isPublic: boolean = true, expiresDays?: number): Promise<ShareLinkResponse> => {
    const response = await apiClient.post(`/api/itinerary/${itineraryId}/share`, {
      is_public: isPublic,
      expires_days: expiresDays,
    })
    return response.data
  },

  getSharedItinerary: async (shareToken: string) => {
    const response = await apiClient.get(`/api/share/${shareToken}`)
    return response.data
  },

  // 临时分享（用于游客用户）
  createTemporaryShare: async (itineraryData: any, expiresDays: number = 7): Promise<ShareLinkResponse> => {
    const response = await apiClient.post('/api/share/temporary', {
      itinerary_data: itineraryData,
      expires_days: expiresDays,
    })
    return response.data
  },

  // PDF导出
  exportItineraryPDF: async (itineraryId: number): Promise<Blob> => {
    const response = await apiClient.get(`/api/itinerary/${itineraryId}/export/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  // 行程编辑
  updateItinerary: async (itineraryId: number, data: {
    agent_name?: string
    destination?: string
    days?: number
    budget?: string
    travelers?: number
    preferences?: string[]
    extra_requirements?: string
  }) => {
    const response = await apiClient.put(`/api/itinerary/${itineraryId}`, data)
    return response.data
  },

  regenerateItinerary: async (itineraryId: number, requestData?: any) => {
    const response = await apiClient.post(`/api/itinerary/${itineraryId}/regenerate`, requestData)
    return response.data
  },

  // 收藏相关
  addFavorite: async (itineraryId: number) => {
    const response = await apiClient.post(`/api/favorites/${itineraryId}`)
    return response.data
  },

  removeFavorite: async (itineraryId: number) => {
    const response = await apiClient.delete(`/api/favorites/${itineraryId}`)
    return response.data
  },

  getFavorites: async (limit: number = 20, offset: number = 0) => {
    const response = await apiClient.get('/api/favorites', {
      params: { limit, offset },
    })
    return response.data
  },

  getFavoriteStatus: async (itineraryId: number) => {
    const response = await apiClient.get(`/api/favorites/${itineraryId}/status`)
    return response.data
  },
}

export default apiClient
