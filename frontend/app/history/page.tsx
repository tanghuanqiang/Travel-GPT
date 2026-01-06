"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Calendar, DollarSign, MapPin, Trash2, Eye, Loader2 } from "lucide-react"
import axios from "axios"

interface HistoryItem {
  id: number
  destination: string
  days: number
  budget: string
  created_at: string
  preview: {
    agentName: string
    travelers: number
    totalBudget: number
  }
}

export default function HistoryPage() {
  const router = useRouter()
  const { user, token, isLoading: authLoading } = useAuth()
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (authLoading) return

    if (!user || !token) {
      router.push("/login")
      return
    }

    loadHistory()
  }, [user, token, authLoading])

  const loadHistory = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get("http://localhost:8000/api/history", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      setHistory(response.data.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || "加载历史记录失败")
    } finally {
      setIsLoading(false)
    }
  }

  const viewItinerary = async (id: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/history/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      // 将数据保存到 localStorage 并跳转到结果页面
      localStorage.setItem('itinerary', JSON.stringify(response.data.itinerary))
      router.push('/result')
    } catch (err: any) {
      alert(err.response?.data?.detail || "加载行程失败")
    }
  }

  const deleteItinerary = async (id: number) => {
    if (!confirm("确定要删除这条历史记录吗？")) return

    try {
      await axios.delete(`http://localhost:8000/api/history/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      // 重新加载列表
      loadHistory()
    } catch (err: any) {
      alert(err.response?.data?.detail || "删除失败")
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <Button variant="ghost" onClick={() => router.push('/')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回首页
          </Button>
          
          <div className="text-sm text-muted-foreground">
            {user?.email}
          </div>
        </div>

        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-3xl">我的旅行历史</CardTitle>
            <CardDescription>查看您之前生成的所有旅行计划</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">
                {error}
              </div>
            )}

            {history.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">还没有历史记录</p>
                <Button onClick={() => router.push('/')}>
                  创建第一个旅行计划
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {history.map((item) => (
                  <Card key={item.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                            <MapPin className="w-5 h-5 text-primary" />
                            {item.destination}
                          </h3>
                          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-3">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {item.days} 天
                            </div>
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              预算: {item.budget || '未设置'}
                            </div>
                            {item.preview.totalBudget && (
                              <div className="flex items-center gap-1">
                                总计: ¥{item.preview.totalBudget}
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            创建时间: {new Date(item.created_at).toLocaleString('zh-CN')}
                          </div>
                        </div>
                        
                        <div className="flex gap-2 ml-4">
                          <Button 
                            size="sm" 
                            onClick={() => viewItinerary(item.id)}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            查看
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deleteItinerary(item.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
