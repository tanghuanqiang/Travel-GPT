"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowLeft, Download, Share2, MapPin, Clock, DollarSign, Star, Sparkles } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"
import Image from "next/image"

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

// 允许的图片域名（仅真实API）
const ALLOWED_IMAGE_DOMAINS = [
  'images.unsplash.com',
  'source.unsplash.com',
  'images.pexels.com',
]

// 验证图片URL是否允许
const isValidImageUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url)
    return ALLOWED_IMAGE_DOMAINS.some(domain => urlObj.hostname === domain)
  } catch {
    return false
  }
}

// 过滤活动图片，只保留允许的域名
const filterValidImages = (images?: string[]): string[] => {
  if (!images || images.length === 0) return []
  return images.filter(isValidImageUrl)
}

export default function ResultPage() {
  const router = useRouter()
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null)

  useEffect(() => {
    const savedData = localStorage.getItem('itinerary')
    if (!savedData) {
      // 如果没有数据，重定向到首页
      router.push('/')
      return
    }
    const data = JSON.parse(savedData)
    
    // 过滤所有活动中的图片，移除不允许的域名
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
  }, [router])

  const handleDownloadPDF = () => {
    alert('PDF导出功能开发中...')
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'TravelPlanGPT - 我的行程',
        text: '查看我的AI生成旅行行程！',
        url: window.location.href
      })
    } else {
      alert('分享链接已复制到剪贴板')
    }
  }

  if (!itinerary) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>加载行程中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
              <span className="text-4xl">🌴</span>
              你的完美行程
            </h1>
            <p className="text-muted-foreground">AI为你精心打造的旅行计划</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => router.push('/')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回
            </Button>
            <Button variant="outline" onClick={handleShare}>
              <Share2 className="w-4 h-4 mr-2" />
              分享
            </Button>
            <Button onClick={handleDownloadPDF}>
              <Download className="w-4 h-4 mr-2" />
              导出PDF
            </Button>
          </div>
        </div>

        {/* Budget Overview */}
        <Card className="mb-8 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-6 h-6" />
              预算总览
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-3xl font-bold text-primary mb-4">
                  ¥{itinerary.overview.totalBudget.toLocaleString()}
                </p>
                <div className="space-y-2">
                  {itinerary.overview.budgetBreakdown.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">{item.category}</span>
                      <span className="font-semibold">¥{item.amount.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={itinerary.overview.budgetBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                      label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
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

        {/* Daily Itinerary */}
        <div className="space-y-8 mb-8">
          <h2 className="text-2xl font-bold">每日行程</h2>
          {itinerary.dailyPlans.map((day) => (
            <Card key={day.day} className="shadow-lg overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-blue-600 text-white">
                <CardTitle className="text-2xl">
                  Day {day.day}: {day.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-6">
                  {day.activities.map((activity, idx) => (
                    <div key={idx} className="border-l-4 border-primary pl-6 relative">
                      <div className="absolute -left-3 top-0 w-6 h-6 bg-primary rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {idx + 1}
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <div className="lg:col-span-2 space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <Clock className="w-4 h-4 text-muted-foreground" />
                                <span className="text-sm text-muted-foreground">{activity.time}</span>
                                <span className="text-sm text-muted-foreground">• {activity.duration}</span>
                              </div>
                              <h3 className="text-xl font-bold">{activity.title}</h3>
                            </div>
                            <div className="text-right">
                              <p className="text-lg font-bold text-primary">¥{activity.cost}</p>
                            </div>
                          </div>

                          <p className="text-muted-foreground">{activity.description}</p>

                          <div className="flex items-start gap-2 text-sm">
                            <MapPin className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                            <span className="text-muted-foreground">{activity.address}</span>
                          </div>

                          <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
                            <p className="text-sm flex items-start gap-2">
                              <Star className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                              <span><strong>为什么推荐：</strong>{activity.reason}</span>
                            </p>
                          </div>
                        </div>

                        {/* Images */}
                        {activity.images && activity.images.length > 0 && (
                          <div className="grid grid-cols-2 gap-2">
                            {activity.images.slice(0, 4).map((img, imgIdx) => (
                              <div key={imgIdx} className="relative aspect-square rounded-lg overflow-hidden">
                                <Image
                                  src={img}
                                  alt={activity.title}
                                  fill
                                  className="object-cover hover:scale-110 transition-transform"
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

        {/* Hidden Gems */}
        {itinerary.hiddenGems && itinerary.hiddenGems.length > 0 && (
          <Card className="mb-8 shadow-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Sparkles className="w-6 h-6 text-purple-600" />
                隐藏宝石 - 本地人才知道的秘密
              </CardTitle>
              <CardDescription>这些小众地点会让你的旅行更加特别</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {itinerary.hiddenGems.map((gem, idx) => (
                  <div key={idx} className="p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg border-2 border-purple-200 dark:border-purple-800">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">💎</span>
                      <div>
                        <h4 className="font-bold mb-1">{gem.title}</h4>
                        <p className="text-sm text-muted-foreground mb-2">{gem.description}</p>
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

        {/* Practical Tips */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl">实用建议</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-bold mb-2 flex items-center gap-2">
                🚇 交通建议
              </h4>
              <p className="text-sm text-muted-foreground">{itinerary.practicalTips.transportation}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 flex items-center gap-2">
                🌤️ 天气提示
              </h4>
              <p className="text-sm text-muted-foreground">{itinerary.practicalTips.weather}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2 flex items-center gap-2">
                🎒 打包清单
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {itinerary.practicalTips.packingList.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-2 flex items-center gap-2">
                📅 季节注意事项
              </h4>
              <p className="text-sm text-muted-foreground">{itinerary.practicalTips.seasonalNotes}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
