"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import {
  ArrowLeft,
  MapPin,
  Clock,
  DollarSign,
  Star,
  Sparkles,
  Loader2,
  AlertCircle,
  Share2,
} from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import Image from "next/image"
import { api } from "@/lib/api"

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

export default function SharePage() {
  const router = useRouter()
  const params = useParams()
  const token = params?.token as string
  
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null)
  const [destination, setDestination] = useState("")
  const [days, setDays] = useState(0)
  const [createdAt, setCreatedAt] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (token) {
      loadSharedItinerary()
    }
  }, [token])

  const loadSharedItinerary = async () => {
    try {
      setIsLoading(true)
      setError("")
      
      const data = await api.getSharedItinerary(token)
      
      // 处理数据
      setDestination(data.destination)
      setDays(data.days)
      setCreatedAt(data.created_at)
      
      const itineraryData = data.itinerary_data
      
      // 过滤图片
      if (itineraryData.dailyPlans) {
        itineraryData.dailyPlans = itineraryData.dailyPlans.map((day: DailyPlan) => ({
          ...day,
          activities: day.activities.map((activity: Activity) => ({
            ...activity,
            images: filterValidImages(activity.images)
          }))
        }))
      }
      
      setItinerary(itineraryData)
    } catch (err: any) {
      console.error('加载分享行程失败:', err)
      if (err.response?.status === 404) {
        setError('分享链接不存在')
      } else if (err.response?.status === 410) {
        setError('分享链接已过期')
      } else {
        setError(err.response?.data?.detail || '加载行程失败，请稍后重试')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `TravelPlanGPT - ${destination} ${days}天行程`,
        text: '查看这个AI生成的旅行行程！',
        url: window.location.href
      }).catch(() => {})
    } else {
      navigator.clipboard.writeText(window.location.href).then(() => {
        alert('链接已复制到剪贴板')
      })
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">加载分享行程中...</p>
        </div>
      </div>
    )
  }

  if (error || !itinerary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-3 mb-2">
              <AlertCircle className="w-6 h-6 text-red-500" />
              <CardTitle className="text-xl">无法加载行程</CardTitle>
            </div>
            <CardDescription>{error || '分享链接无效'}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={() => router.push('/')} className="w-full">
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回首页
            </Button>
          </CardContent>
        </Card>
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
              onClick={() => router.push('/')}
              className="flex-shrink-0"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            
            <div className="flex-1 text-center">
              <h1 className="text-sm sm:text-base font-semibold truncate">
                {destination} {days}天行程
              </h1>
              <p className="text-xs text-muted-foreground">分享的行程</p>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleShare}
              className="flex-shrink-0"
            >
              <Share2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-4 sm:py-6 max-w-4xl">
        {/* 分享提示 */}
        <Card className="mb-4 sm:mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="pt-4 sm:pt-6">
            <div className="flex items-start gap-3">
              <Share2 className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm sm:text-base font-medium text-blue-900 dark:text-blue-100">
                  这是分享的行程
                </p>
                <p className="text-xs sm:text-sm text-blue-700 dark:text-blue-300 mt-1">
                  由 TravelPlanGPT 生成 • {new Date(createdAt).toLocaleDateString('zh-CN')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

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
                      <span className="text-xl sm:text-2xl">💎</span>
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
        <Card className="shadow-lg mb-4 sm:mb-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg sm:text-2xl">实用建议</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                🚇 交通建议
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.transportation}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                🌤️ 天气提示
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.weather}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                🎒 打包清单
              </h4>
              <ul className="text-xs sm:text-sm text-muted-foreground space-y-1">
                {itinerary.practicalTips.packingList.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-2 text-sm sm:text-base flex items-center gap-2">
                📅 季节注意事项
              </h4>
              <p className="text-xs sm:text-sm text-muted-foreground">{itinerary.practicalTips.seasonalNotes}</p>
            </div>
          </CardContent>
        </Card>

        {/* 底部提示 */}
        <Card className="bg-gradient-to-r from-orange-500 to-blue-600 text-white shadow-lg">
          <CardContent className="pt-6 pb-6 text-center">
            <h3 className="text-lg sm:text-xl font-bold mb-2">想要创建自己的行程？</h3>
            <p className="text-sm sm:text-base mb-4 opacity-90">
              使用 TravelPlanGPT 为你生成个性化的旅行计划
            </p>
            <Button
              onClick={() => router.push('/')}
              variant="secondary"
              size="lg"
              className="bg-white text-primary hover:bg-gray-100"
            >
              立即开始规划
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
