"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, Calendar, DollarSign, MapPin, Trash2, Eye, Loader2, Heart, Search, Filter, X } from "lucide-react"
import axios from "axios"

interface HistoryItem {
  id: number
  destination: string
  days: number
  budget: string
  created_at: string
  is_favorited?: boolean
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
  
  // 搜索、筛选、排序状态
  const [searchQuery, setSearchQuery] = useState("")
  const [minDays, setMinDays] = useState<number | undefined>(undefined)
  const [maxDays, setMaxDays] = useState<number | undefined>(undefined)
  const [minBudget, setMinBudget] = useState<number | undefined>(undefined)
  const [maxBudget, setMaxBudget] = useState<number | undefined>(undefined)
  const [sortBy, setSortBy] = useState<"created_at" | "total_budget" | "days">("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    if (authLoading) return

    if (!user || !token) {
      router.push("/login")
      return
    }

    // 初始加载（不包含搜索/筛选参数）
    // 搜索/筛选会触发另一个useEffect
  }, [user, token, authLoading, router])

  const loadHistory = async () => {
    try {
      setIsLoading(true)
      const params: any = {
        limit: 100, // 获取更多数据以便前端筛选
        offset: 0,
      }
      
      // 添加搜索参数
      if (searchQuery.trim()) {
        params.search = searchQuery.trim()
      }
      
      // 添加筛选参数
      if (minDays !== undefined) {
        params.min_days = minDays
      }
      if (maxDays !== undefined) {
        params.max_days = maxDays
      }
      if (minBudget !== undefined) {
        params.min_budget = minBudget
      }
      if (maxBudget !== undefined) {
        params.max_budget = maxBudget
      }
      
      // 添加排序参数
      params.sort_by = sortBy
      params.sort_order = sortOrder
      
      const response = await axios.get("http://localhost:8000/api/history", {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params
      })
      setHistory(response.data.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || "加载历史记录失败")
    } finally {
      setIsLoading(false)
    }
  }
  
  // 当搜索、筛选、排序参数变化时重新加载
  useEffect(() => {
    if (user && token && !authLoading) {
      loadHistory()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, minDays, maxDays, minBudget, maxBudget, sortBy, sortOrder, user, token, authLoading])
  
  const clearFilters = () => {
    setSearchQuery("")
    setMinDays(undefined)
    setMaxDays(undefined)
    setMinBudget(undefined)
    setMaxBudget(undefined)
    setSortBy("created_at")
    setSortOrder("desc")
  }
  
  const hasActiveFilters = searchQuery || minDays !== undefined || maxDays !== undefined || minBudget !== undefined || maxBudget !== undefined

  const viewItinerary = async (id: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/history/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      localStorage.setItem('itinerary', JSON.stringify(response.data.itinerary))
      router.push(`/result?id=${id}`)
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
      
      loadHistory()
    } catch (err: any) {
      alert(err.response?.data?.detail || "删除失败")
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* 移动端优化的顶部导航栏 */}
      <div className="sticky top-0 z-40 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/')}
              className="flex-shrink-0"
            >
              <ArrowLeft className="w-4 h-4 mr-1 sm:mr-2" />
              <span className="hidden sm:inline">返回首页</span>
              <span className="sm:hidden">返回</span>
            </Button>
            
            <h1 className="text-base sm:text-lg font-bold flex-1 text-center truncate">
              我的旅行历史
            </h1>
            
            <div className="text-xs sm:text-sm text-muted-foreground flex-shrink-0 max-w-[100px] sm:max-w-none truncate">
              {user?.email}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-4 sm:py-6 max-w-4xl">
        <Card className="shadow-xl">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl sm:text-2xl lg:text-3xl">我的旅行历史</CardTitle>
            <CardDescription className="text-sm sm:text-base">查看您之前生成的所有旅行计划</CardDescription>
          </CardHeader>
          <CardContent>
            {/* 搜索和筛选栏 */}
            <div className="mb-6 space-y-4">
              {/* 搜索框 */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  type="text"
                  placeholder="搜索目的地或行程名称..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              {/* 排序和筛选按钮 */}
              <div className="flex flex-wrap gap-2 items-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-2"
                >
                  <Filter className="w-4 h-4" />
                  筛选
                </Button>
                
                <div className="flex items-center gap-2">
                  <Label className="text-sm text-muted-foreground">排序:</Label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as "created_at" | "total_budget" | "days")}
                    className="px-3 py-1.5 text-sm border rounded-md bg-background"
                  >
                    <option value="created_at">创建时间</option>
                    <option value="total_budget">预算</option>
                    <option value="days">天数</option>
                  </select>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                    className="px-2"
                  >
                    {sortOrder === "asc" ? "↑" : "↓"}
                  </Button>
                </div>
                
                {hasActiveFilters && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearFilters}
                    className="flex items-center gap-1 text-muted-foreground"
                  >
                    <X className="w-4 h-4" />
                    清除筛选
                  </Button>
                )}
              </div>
              
              {/* 筛选面板 */}
              {showFilters && (
                <Card className="p-4 bg-gray-50 dark:bg-gray-800/50">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* 天数筛选 */}
                    <div className="space-y-2">
                      <Label className="text-sm">天数范围</Label>
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          placeholder="最小天数"
                          value={minDays || ""}
                          onChange={(e) => setMinDays(e.target.value ? parseInt(e.target.value) : undefined)}
                          min="1"
                          max="5"
                          className="flex-1"
                        />
                        <span className="self-center text-muted-foreground">-</span>
                        <Input
                          type="number"
                          placeholder="最大天数"
                          value={maxDays || ""}
                          onChange={(e) => setMaxDays(e.target.value ? parseInt(e.target.value) : undefined)}
                          min="1"
                          max="5"
                          className="flex-1"
                        />
                      </div>
                    </div>
                    
                    {/* 预算筛选 */}
                    <div className="space-y-2">
                      <Label className="text-sm">预算范围 (¥)</Label>
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          placeholder="最小预算"
                          value={minBudget || ""}
                          onChange={(e) => setMinBudget(e.target.value ? parseFloat(e.target.value) : undefined)}
                          min="0"
                          className="flex-1"
                        />
                        <span className="self-center text-muted-foreground">-</span>
                        <Input
                          type="number"
                          placeholder="最大预算"
                          value={maxBudget || ""}
                          onChange={(e) => setMaxBudget(e.target.value ? parseFloat(e.target.value) : undefined)}
                          min="0"
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                </Card>
              )}
            </div>
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm mb-4 border border-red-200 dark:border-red-800">
                {error}
              </div>
            )}

            {history.length === 0 ? (
              <div className="text-center py-12 sm:py-16">
                <p className="text-muted-foreground mb-4 text-sm sm:text-base">还没有历史记录</p>
                <Button onClick={() => router.push('/')} size="lg">
                  创建第一个旅行计划
                </Button>
              </div>
            ) : (
              <div className="space-y-3 sm:space-y-4">
                {history.map((item) => (
                  <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => viewItinerary(item.id)}>
                    <CardContent className="p-4 sm:p-6">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg sm:text-xl font-bold mb-2 flex items-center gap-2">
                            <MapPin className="w-4 h-4 sm:w-5 sm:h-5 text-primary flex-shrink-0" />
                            <span className="truncate">{item.destination}</span>
                            {item.is_favorited && (
                              <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-red-500 fill-red-500 flex-shrink-0" />
                            )}
                          </h3>
                          <div className="flex flex-wrap gap-3 sm:gap-4 text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-3">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
                              <span>{item.days} 天</span>
                            </div>
                            {item.budget && (
                              <div className="flex items-center gap-1">
                                <DollarSign className="w-3 h-3 sm:w-4 sm:h-4" />
                                <span>预算: {item.budget}</span>
                              </div>
                            )}
                            {item.preview?.totalBudget && (
                              <div className="flex items-center gap-1">
                                <span>总计: ¥{item.preview.totalBudget.toLocaleString()}</span>
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            创建时间: {new Date(item.created_at).toLocaleString('zh-CN', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </div>
                        
                        <div className="flex gap-2 sm:gap-2 sm:ml-4 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                          <Button 
                            size="sm" 
                            onClick={(e) => {
                              e.stopPropagation()
                              viewItinerary(item.id)
                            }}
                            className="flex-1 sm:flex-none"
                          >
                            <Eye className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                            <span className="text-xs sm:text-sm">查看</span>
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={(e) => {
                              e.stopPropagation()
                              deleteItinerary(item.id)
                            }}
                            className="px-2 sm:px-3"
                          >
                            <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
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
