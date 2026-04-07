"use client"

import { useEffect, useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  ArrowLeft,
  Download,
  Share2,
  MapPin,
  Clock,
  DollarSign,
  Star,
  Sparkles,
  Edit,
  Copy,
  Check,
  Loader2,
  Heart,
  RefreshCw,
  Gem,
  Train,
  CloudSun,
  Backpack,
  CalendarCheck,
} from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import Image from "next/image"
import { api } from "@/lib/api"
import axios from "axios"

interface Activity {
  time: string
  title: string
  description: string
  duration: string
  cost: number
  address: string
  reason: string
  images?: string[]
}

interface DailyPlan {
  day: number
  title: string
  activities: Activity[]
}

interface ItineraryData {
  destination?: string  // 可选：目的地
  days?: number  // 可选：天数
  overview: {
    totalBudget: number
    budgetBreakdown: {
      category: string
      amount: number
    }[]
  }
  dailyPlans: DailyPlan[]
  hiddenGems: {
    title: string
    description: string
    category: string
  }[]
  practicalTips: {
    transportation: string
    packingList: string[]
    weather: string
    seasonalNotes: string
  }
}

const COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']

// 允许的图片域名
const ALLOWED_IMAGE_DOMAINS = [
  'images.unsplash.com',
  'source.unsplash.com',
  'images.pexels.com',
]

const isValidImageUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url)
    return ALLOWED_IMAGE_DOMAINS.some(domain => urlObj.hostname === domain)
  } catch {
    return false
  }
}

const filterValidImages = (images?: string[]): string[] => {
  if (!images || images.length === 0) return []
  return images.filter(isValidImageUrl)
}

// 内部组件：使用 useSearchParams
function ResultPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, token } = useAuth()
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null)
  const [itineraryId, setItineraryId] = useState<number | null>(null)
  const [shareToken, setShareToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  // 分享对话框状态
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [shareLink, setShareLink] = useState("")
  const [shareLinkCopied, setShareLinkCopied] = useState(false)
  const [creatingShareLink, setCreatingShareLink] = useState(false)
  
  // 编辑对话框状态
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editFormData, setEditFormData] = useState({
    agent_name: "",
    destination: "",
    days: 2,
    budget: "",
    travelers: 2,
    extra_requirements: "",
  })
  const [isEditing, setIsEditing] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  
  // 收藏状态
  const [isFavorite, setIsFavorite] = useState(false)
  const [checkingFavorite, setCheckingFavorite] = useState(false)

  useEffect(() => {
    loadItinerary()
  }, [searchParams, user, token])

  const loadItinerary = async () => {
    try {
      setIsLoading(true)
      
      // 优先级1: 从URL参数获取token（临时分享链接或游客用户）
      const tokenParam = searchParams?.get('token')
      if (tokenParam) {
        try {
          // 从API获取分享的行程
          const shareData = await api.getSharedItinerary(tokenParam)
          const data = shareData.itinerary_data
          processItineraryData(data)
          setShareToken(tokenParam) // 保存分享token用于PDF导出
          
          // 如果是登录用户且是永久分享，可以检查收藏状态
          if (shareData.id && user && token) {
            setItineraryId(shareData.id)
            checkFavoriteStatus(shareData.id)
          }
          return
        } catch (shareErr: any) {
          console.error('加载分享行程失败:', shareErr)
          // 如果分享链接无效，继续尝试其他方式
        }
      }
      
      // 优先级2: 从URL参数获取itinerary_id（从历史记录页跳转的登录用户）
      const idParam = searchParams?.get('id')
      if (idParam && user && token) {
        const id = parseInt(idParam)
        setItineraryId(id)
        
        // 从API获取行程详情
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18890'
        const response = await axios.get(`${apiUrl}/api/history/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        const data = response.data.itinerary
        processItineraryData(data)
        
        // 检查收藏状态
        checkFavoriteStatus(id)
        return
      }
      
      // 优先级3: 从localStorage获取（向后兼容，仅用于没有token的情况）
      const savedData = localStorage.getItem('itinerary')
      if (savedData) {
        const data = JSON.parse(savedData)
        processItineraryData(data)
        return
      }
      
      // 如果都没有，跳转到首页
      router.push('/')
    } catch (err: any) {
      console.error('加载行程失败:', err)
      // 如果所有方式都失败，尝试从localStorage加载（最后的后备方案）
      const savedData = localStorage.getItem('itinerary')
      if (savedData) {
        const data = JSON.parse(savedData)
        processItineraryData(data)
      } else {
        router.push('/')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const processItineraryData = (data: any) => {
    // 过滤图片
    if (data.dailyPlans) {
      data.dailyPlans = data.dailyPlans.map((day: DailyPlan) => ({
        ...day,
        activities: day.activities.map((activity: Activity) => ({
          ...activity,
          images: filterValidImages(activity.images)
        }))
      }))
    }
    setItinerary(data)
    
    // 设置编辑表单初始值（如果有基础信息）
    if (data.destination || data.agent_name) {
      setEditFormData({
        agent_name: data.agent_name || "",
        destination: data.destination || "",
        days: data.days || 2,
        budget: data.budget || "",
        travelers: data.travelers || 2,
        extra_requirements: data.extra_requirements || "",
      })
    }
  }

  const checkFavoriteStatus = async (id: number) => {
    if (!user || !token) return
    
    try {
      setCheckingFavorite(true)
      const status = await api.getFavoriteStatus(id)
      setIsFavorite(status.is_favorited || false)
    } catch (err) {
      console.error('检查收藏状态失败:', err)
      setIsFavorite(false)
    } finally {
      setCheckingFavorite(false)
    }
  }

  // PDF导出
  const handleDownloadPDF = async () => {
    if (!itinerary) {
      alert('行程数据不存在，无法导出PDF')
      return
    }

    try {
      let blob: Blob
      
      // 优先级1: 登录用户且已保存的行程
      if (itineraryId && user && token) {
        blob = await api.exportItineraryPDF(itineraryId)
      }
      // 优先级2: 从分享链接查看的行程
      else if (shareToken) {
        blob = await api.exportSharedItineraryPDF(shareToken)
      }
      // 优先级3: 游客用户的本地行程数据
      else {
        const destination = itinerary.destination || "未知目的地"
        const days = itinerary.days || itinerary.dailyPlans?.length || 2
        blob = await api.exportPDFFromData(itinerary, destination, days)
      }
      
      // 下载PDF文件
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const destination = itinerary.destination || "未知目的地"
      const days = itinerary.days || itinerary.dailyPlans?.length || 2
      a.download = `${destination}_${days}天行程.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      console.error('PDF导出失败:', err)
      alert(err.response?.data?.detail || 'PDF导出失败，请稍后重试')
    }
  }

  // 分享功能
  const handleShare = async () => {
    setShareDialogOpen(true)
    setCreatingShareLink(true)
    
    try {
      if (!itineraryId || !user || !token) {
        // 游客用户：创建临时分享链接
        if (!itinerary) {
          alert('行程数据不存在，无法分享')
          setShareDialogOpen(false)
          return
        }
        
        // 从localStorage获取原始请求参数，包含destination和days
        const travelPlan = localStorage.getItem('travelPlan')
        let shareDataToSend: ItineraryData & { destination?: string; days?: number } = { ...itinerary }
        
        if (travelPlan) {
          try {
            const planData = JSON.parse(travelPlan)
            // 将destination和days添加到分享数据中
            shareDataToSend.destination = planData.destination || ""
            shareDataToSend.days = planData.days || itinerary.dailyPlans?.length || 2
          } catch (e) {
            // 如果解析失败，使用默认值
            shareDataToSend.destination = ""
            shareDataToSend.days = itinerary.dailyPlans?.length || 2
          }
        } else {
          shareDataToSend.destination = ""
          shareDataToSend.days = itinerary.dailyPlans?.length || 2
        }
        
        const shareData = await api.createTemporaryShare(shareDataToSend, 7) // 7天过期
        const fullUrl = `${window.location.origin}/share/${shareData.share_token}`
        setShareLink(fullUrl)
      } else {
        // 登录用户：创建永久分享链接
        const shareData = await api.createShareLink(itineraryId, true)
        const fullUrl = `${window.location.origin}/share/${shareData.share_token}`
        setShareLink(fullUrl)
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || '创建分享链接失败')
      setShareDialogOpen(false)
    } finally {
      setCreatingShareLink(false)
    }
  }

  const copyShareLink = () => {
    navigator.clipboard.writeText(shareLink).then(() => {
      setShareLinkCopied(true)
      setTimeout(() => setShareLinkCopied(false), 2000)
    })
  }

  // 编辑功能
  const handleEdit = () => {
    if (!itineraryId || !user || !token) {
      alert('请先登录并保存行程后才能编辑')
      return
    }
    setEditDialogOpen(true)
  }

  const handleUpdateItinerary = async () => {
    if (!itineraryId) return

    try {
      setIsEditing(true)
      await api.updateItinerary(itineraryId, editFormData)
      alert('行程信息已更新')
      setEditDialogOpen(false)
      // 重新加载行程
      await loadItinerary()
    } catch (err: any) {
      alert(err.response?.data?.detail || '更新失败，请稍后重试')
    } finally {
      setIsEditing(false)
    }
  }

  const handleRegenerateItinerary = async () => {
    if (!itineraryId) return

    if (!confirm('确定要重新生成行程吗？这将使用AI重新规划整个行程。')) {
      return
    }

    try {
      setIsRegenerating(true)
      const newItinerary = await api.regenerateItinerary(itineraryId, editFormData)
      processItineraryData(newItinerary)
      setEditDialogOpen(false)
      alert('行程已重新生成')
    } catch (err: any) {
      alert(err.response?.data?.detail || '重新生成失败，请稍后重试')
    } finally {
      setIsRegenerating(false)
    }
  }

  // 收藏功能
  const toggleFavorite = async () => {
    if (!itineraryId || !user || !token) {
      alert('请先登录')
      return
    }

    try {
      if (isFavorite) {
        await api.removeFavorite(itineraryId)
        setIsFavorite(false)
      } else {
        await api.addFavorite(itineraryId)
        setIsFavorite(true)
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || '操作失败，请稍后重试')
    }
  }

  if (isLoading || !itinerary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">加载行程中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* 移动端优化的顶部导航栏 */}
      <div className="sticky top-0 z-40 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                // 如果有itineraryId，说明是从历史记录页面跳转的，返回历史记录页面
                // 否则返回首页
                if (itineraryId && user) {
                  router.push('/history')
                } else {
                  router.push('/')
                }
              }}
              className="flex-shrink-0"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            
            <h1 className="text-lg font-bold truncate flex-1 text-center">
              {editFormData.agent_name || '我的行程'}
            </h1>
            
            <div className="flex items-center gap-1 flex-shrink-0">
              {itineraryId && user && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleFavorite}
                    disabled={checkingFavorite}
                    className="p-2"
                  >
                    <Heart className={`w-4 h-4 ${isFavorite ? 'fill-red-500 text-red-500' : ''}`} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleEdit}
                    className="p-2"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                </>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleShare}
                className="p-2"
              >
                <Share2 className="w-4 h-4" />
              </Button>
              {itinerary && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDownloadPDF}
                  className="p-2"
                  title="导出PDF"
                >
                  <Download className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-4 sm:py-6 max-w-4xl">
        {/* 预算总览 - 移动端优化 */}
        <Card className="mb-4 sm:mb-6 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <DollarSign className="w-5 h-5" />
              预算总览
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <p className="text-2xl sm:text-3xl font-bold text-primary mb-3 sm:mb-4">
                  ¥{itinerary.overview.totalBudget.toLocaleString()}
                </p>
                <div className="space-y-2">
                  {itinerary.overview.budgetBreakdown.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm sm:text-base">
                      <span className="text-muted-foreground">{item.category}</span>
                      <span className="font-semibold">¥{item.amount.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-center min-h-[200px]">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={itinerary.overview.budgetBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="amount"
                      label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                    >
                      {itinerary.overview.budgetBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 每日行程 - 移动端优化 */}
        <div className="space-y-4 sm:space-y-6 mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold px-2">每日行程</h2>
          {itinerary.dailyPlans.map((day) => (
            <Card key={day.day} className="shadow-lg overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-blue-600 text-white py-3 sm:py-4">
                <CardTitle className="text-lg sm:text-2xl">
                  第{day.day}天: {day.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 sm:pt-6 px-3 sm:px-6">
                <div className="space-y-4 sm:space-y-6">
                  {day.activities.map((activity, idx) => (
                    <div key={idx} className="border-l-4 border-primary pl-3 sm:pl-6 relative">
                      <div className="absolute -left-3 sm:-left-3 top-0 w-5 h-5 sm:w-6 sm:h-6 bg-primary rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {idx + 1}
                      </div>
                      
                      <div className="space-y-2 sm:space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1 text-xs sm:text-sm text-muted-foreground">
                              <Clock className="w-3 h-3 sm:w-4 sm:h-4" />
                              <span>{activity.time}</span>
                              <span>•</span>
                              <span>{activity.duration}</span>
                            </div>
                            <h3 className="text-base sm:text-xl font-bold mb-1">{activity.title}</h3>
                          </div>
                          <div className="text-right">
                            <p className="text-base sm:text-lg font-bold text-primary">¥{activity.cost}</p>
                          </div>
                        </div>

                        <p className="text-sm sm:text-base text-muted-foreground">{activity.description}</p>

                        <div className="flex items-start gap-2 text-xs sm:text-sm">
                          <MapPin className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                          <span className="text-muted-foreground">{activity.address}</span>
                        </div>

                        <div className="bg-orange-50 dark:bg-orange-900/20 p-2 sm:p-3 rounded-lg">
                          <p className="text-xs sm:text-sm flex items-start gap-2">
                            <Star className="w-3 h-3 sm:w-4 sm:h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                            <span><strong>推荐理由：</strong>{activity.reason}</span>
                          </p>
                        </div>

                        {/* 图片 - 移动端单列，桌面端网格 */}
                        {activity.images && activity.images.length > 0 && (
                          <div className="grid grid-cols-2 sm:grid-cols-2 gap-2 mt-2">
                            {activity.images.slice(0, 4).map((img, imgIdx) => (
                              <div key={imgIdx} className="relative aspect-square rounded-lg overflow-hidden">
                                <Image
                                  src={img}
                                  alt={activity.title}
                                  fill
                                  className="object-cover"
                                  sizes="(max-width: 640px) 50vw, 200px"
                                />
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 隐藏宝石 - 移动端优化 */}
        {itinerary.hiddenGems && itinerary.hiddenGems.length > 0 && (
          <Card className="mb-4 sm:mb-6 shadow-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-2xl">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
                隐藏宝石
              </CardTitle>
              <CardDescription className="text-xs sm:text-sm">本地人才知道的秘密地点</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {itinerary.hiddenGems.map((gem, idx) => (
                  <div key={idx} className="p-3 sm:p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg border-2 border-purple-200 dark:border-purple-800">
                    <div className="flex items-start gap-2 sm:gap-3">
                      <Gem className="w-6 h-6 sm:w-8 sm:h-8 text-purple-600 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-bold mb-1 text-sm sm:text-base">{gem.title}</h4>
                        <p className="text-xs sm:text-sm text-muted-foreground mb-2">{gem.description}</p>
                        <span className="inline-block px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-xs">
                          {gem.category}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 实用建议 - 移动端优化 */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg sm:text-2xl">实用建议</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                <Train className="w-4 h-4 text-blue-500" />
                交通建议
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.transportation}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                <CloudSun className="w-4 h-4 text-yellow-500" />
                天气提示
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.weather}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                <Backpack className="w-4 h-4 text-orange-500" />
                打包清单
              </h4>
              <ul className="text-xs sm:text-sm text-muted-foreground space-y-1">
                {itinerary.practicalTips.packingList.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                <CalendarCheck className="w-4 h-4 text-green-500" />
                季节注意事项
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.seasonalNotes}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 分享对话框 */}
      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>分享行程</DialogTitle>
            <DialogDescription>
              复制链接分享给朋友，他们可以通过链接查看你的行程
            </DialogDescription>
          </DialogHeader>
          {creatingShareLink ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={shareLink}
                  readOnly
                  className="flex-1"
                />
                <Button
                  onClick={copyShareLink}
                  variant="outline"
                  size="icon"
                >
                  {shareLinkCopied ? (
                    <Check className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
              </div>
              {shareLinkCopied && (
                <p className="text-sm text-green-600 text-center">已复制到剪贴板</p>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShareDialogOpen(false)}>
              关闭
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑对话框 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>编辑行程</DialogTitle>
            <DialogDescription>
              修改行程基本信息，或重新生成完整行程
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="agent_name">行程名称</Label>
              <Input
                id="agent_name"
                value={editFormData.agent_name}
                onChange={(e) => setEditFormData({ ...editFormData, agent_name: e.target.value })}
                placeholder="我的周末旅行"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="destination">目的地</Label>
              <Input
                id="destination"
                value={editFormData.destination}
                onChange={(e) => setEditFormData({ ...editFormData, destination: e.target.value })}
                placeholder="例如：上海"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="days">天数</Label>
                <Input
                  id="days"
                  type="number"
                  min="1"
                  max="5"
                  value={editFormData.days}
                  onChange={(e) => setEditFormData({ ...editFormData, days: parseInt(e.target.value) || 2 })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="travelers">人数</Label>
                <Input
                  id="travelers"
                  type="number"
                  min="1"
                  value={editFormData.travelers}
                  onChange={(e) => setEditFormData({ ...editFormData, travelers: parseInt(e.target.value) || 2 })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">预算</Label>
              <Input
                id="budget"
                value={editFormData.budget}
                onChange={(e) => setEditFormData({ ...editFormData, budget: e.target.value })}
                placeholder="例如：2000-5000元"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="extra_requirements">额外要求</Label>
              <Textarea
                id="extra_requirements"
                value={editFormData.extra_requirements}
                onChange={(e) => setEditFormData({ ...editFormData, extra_requirements: e.target.value })}
                placeholder="例如：避免热门景点、多安排拍照点..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={() => setEditDialogOpen(false)}
              className="w-full sm:w-auto"
            >
              取消
            </Button>
            <Button
              onClick={handleUpdateItinerary}
              disabled={isEditing}
              className="w-full sm:w-auto"
            >
              {isEditing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  更新中...
                </>
              ) : (
                '保存修改'
              )}
            </Button>
            <Button
              onClick={handleRegenerateItinerary}
              disabled={isRegenerating}
              variant="default"
              className="w-full sm:w-auto"
            >
              {isRegenerating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  重新生成
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// 主组件：用 Suspense 包裹
export default function ResultPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">加载中...</p>
          </div>
        </div>
      }
    >
      <ResultPageContent />
    </Suspense>
  )
}
