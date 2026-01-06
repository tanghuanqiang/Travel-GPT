"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plane, MapPin, Calendar, Users, DollarSign, Sparkles, ArrowRight, Heart, Camera, Utensils, Building, ShoppingBag, Mountain, LogIn, History, LogOut, User } from "lucide-react"

interface TravelFormData {
  agentName: string
  destination: string
  days: number
  budget: string
  travelers: number
  preferences: string[]
  extraRequirements: string
}

const presetExamples = [
  {
    title: "上海2天美食之旅",
    destination: "上海",
    days: 2,
    budget: "3000元",
    preferences: ["美食"],
    icon: "🍜"
  },
  {
    title: "成都周末户外放松",
    destination: "成都",
    days: 3,
    budget: "2500元",
    preferences: ["户外", "美食"],
    icon: "🏔️"
  },
  {
    title: "京都3天文化体验",
    destination: "京都",
    days: 3,
    budget: "5000元",
    preferences: ["文化", "购物"],
    icon: "⛩️"
  }
]

const preferenceOptions = [
  { label: "美食", value: "food", icon: "🍽️" },
  { label: "户外", value: "outdoor", icon: "🏞️" },
  { label: "购物", value: "shopping", icon: "🛍️" },
  { label: "文化", value: "culture", icon: "🎭" },
  { label: "放松", value: "relax", icon: "🧘" },
  { label: "冒险", value: "adventure", icon: "🎢" },
  { label: "亲子", value: "family", icon: "👨‍👩‍👧" },
]

export default function HomePage() {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [formData, setFormData] = useState<TravelFormData>({
    agentName: "我的周末旅行",
    destination: "",
    days: 2,
    budget: "",
    travelers: 2,
    preferences: [],
    extraRequirements: ""
  })

  const handlePreferenceToggle = (value: string) => {
    setFormData(prev => ({
      ...prev,
      preferences: prev.preferences.includes(value)
        ? prev.preferences.filter(p => p !== value)
        : [...prev.preferences, value]
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // 将表单数据存储到localStorage或状态管理
    localStorage.setItem('travelPlan', JSON.stringify(formData))
    router.push('/plan')
  }

  const loadPreset = (preset: typeof presetExamples[0]) => {
    setFormData({
      ...formData,
      destination: preset.destination,
      days: preset.days,
      budget: preset.budget,
      preferences: preset.preferences
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* User Navigation */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-end gap-2">
          {user ? (
            <>
              <Button variant="ghost" size="sm" className="gap-2">
                <User className="w-4 h-4" />
                {user.email}
              </Button>
              <Button variant="ghost" size="sm" onClick={() => router.push('/history')} className="gap-2">
                <History className="w-4 h-4" />
                历史记录
              </Button>
              <Button variant="ghost" size="sm" onClick={logout} className="gap-2">
                <LogOut className="w-4 h-4" />
                退出
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" onClick={() => router.push('/login')} className="gap-2">
                <LogIn className="w-4 h-4" />
                登录
              </Button>
              <Button size="sm" onClick={() => router.push('/register')} className="gap-2">
                注册
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Plane className="w-12 h-12 text-primary animate-pulse" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-orange-500 to-blue-600 bg-clip-text text-transparent">
              TravelPlanGPT
            </h1>
            <Sparkles className="w-12 h-12 text-blue-500 animate-pulse" />
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            输入你的旅行需求，AI将为你生成一份完美的周末行程！🚀
          </p>
          {user && (
            <p className="text-sm text-muted-foreground mt-2">
              💾 登录状态下生成的行程将自动保存到历史记录
            </p>
          )}
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <Card className="shadow-2xl border-2">
              <CardHeader>
                <CardTitle className="text-2xl">创建你的旅行计划</CardTitle>
                <CardDescription>填写下方信息，让AI为你规划专属行程</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Agent Name */}
                  <div className="space-y-2">
                    <Label htmlFor="agentName">行程名称（可选）</Label>
                    <Input
                      id="agentName"
                      placeholder="例如：我的周末旅行"
                      value={formData.agentName}
                      onChange={(e) => setFormData({...formData, agentName: e.target.value})}
                    />
                  </div>

                  {/* Destination */}
                  <div className="space-y-2">
                    <Label htmlFor="destination" className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      目的地城市 <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="destination"
                      placeholder="例如：上海、东京、巴黎"
                      value={formData.destination}
                      onChange={(e) => setFormData({...formData, destination: e.target.value})}
                      required
                    />
                  </div>

                  {/* Days and Travelers */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="days" className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        旅行天数
                      </Label>
                      <Input
                        id="days"
                        type="number"
                        min="1"
                        max="5"
                        value={formData.days}
                        onChange={(e) => setFormData({...formData, days: parseInt(e.target.value)})}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="travelers" className="flex items-center gap-2">
                        <Users className="w-4 h-4" />
                        出行人数
                      </Label>
                      <Input
                        id="travelers"
                        type="number"
                        min="1"
                        value={formData.travelers}
                        onChange={(e) => setFormData({...formData, travelers: parseInt(e.target.value)})}
                      />
                    </div>
                  </div>

                  {/* Budget */}
                  <div className="space-y-2">
                    <Label htmlFor="budget" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      预算范围
                    </Label>
                    <Input
                      id="budget"
                      placeholder="例如：2000-5000元"
                      value={formData.budget}
                      onChange={(e) => setFormData({...formData, budget: e.target.value})}
                    />
                  </div>

                  {/* Preferences */}
                  <div className="space-y-2">
                    <Label>偏好标签（多选）</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {preferenceOptions.map((pref) => (
                        <Button
                          key={pref.value}
                          type="button"
                          variant={formData.preferences.includes(pref.value) ? "default" : "outline"}
                          className="justify-start"
                          onClick={() => handlePreferenceToggle(pref.value)}
                        >
                          <span className="mr-2">{pref.icon}</span>
                          {pref.label}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Extra Requirements */}
                  <div className="space-y-2">
                    <Label htmlFor="extra">额外要求（可选）</Label>
                    <Textarea
                      id="extra"
                      placeholder="例如：避免热门景点、多安排拍照点、素食友好..."
                      value={formData.extraRequirements}
                      onChange={(e) => setFormData({...formData, extraRequirements: e.target.value})}
                      rows={3}
                    />
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                    disabled={!formData.destination}
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    生成行程
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Preset Examples Sidebar */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">快速开始 ✨</h3>
            {presetExamples.map((preset, index) => (
              <Card
                key={index}
                className="cursor-pointer hover:shadow-lg transition-all hover:scale-105"
                onClick={() => loadPreset(preset)}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <span className="text-2xl">{preset.icon}</span>
                    {preset.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  <div className="space-y-1">
                    <p>📍 {preset.destination}</p>
                    <p>📅 {preset.days}天</p>
                    <p>💰 {preset.budget}</p>
                    <div className="flex gap-1 flex-wrap mt-2">
                      {preset.preferences.map(p => (
                        <span key={p} className="px-2 py-1 bg-primary/10 rounded text-xs">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
