"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plane, MapPin, Calendar, Users, DollarSign, Sparkles, LogIn, History, LogOut, User, Menu, X, Utensils, Mountain, ShoppingBag, Theater, Leaf, Compass, Baby, Map } from "lucide-react"

interface TravelFormData {
  agentName: string
  destination: string
  days: string
  budget: string
  travelers: string
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
    icon: "utensils"
  },
  {
    title: "成都周末户外放松",
    destination: "成都",
    days: 3,
    budget: "2500元",
    preferences: ["户外", "美食"],
    icon: "mountain"
  },
  {
    title: "京都3天文化体验",
    destination: "京都",
    days: 3,
    budget: "5000元",
    preferences: ["文化", "购物"],
    icon: "landmark"
  }
]

const preferenceOptions = [
  { label: "美食", value: "food", icon: "Utensils" },
  { label: "户外", value: "outdoor", icon: "Mountain" },
  { label: "购物", value: "shopping", icon: "ShoppingBag" },
  { label: "文化", value: "culture", icon: "Theater" },
  { label: "放松", value: "relax", icon: "Leaf" },
  { label: "冒险", value: "adventure", icon: "Compass" },
  { label: "亲子", value: "family", icon: "Baby" },
]

export default function HomePage() {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [formData, setFormData] = useState<TravelFormData>({
    agentName: "我的周末旅行",
    destination: "",
    days: "2",
    budget: "",
    travelers: "2",
    preferences: [],
    extraRequirements: ""
  })
  const [showMobileMenu, setShowMobileMenu] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/')
  }

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
    
    // 校验必填字段
    if (!formData.destination.trim()) {
      alert("请输入目的地城市")
      return
    }
    
    if (!formData.days.trim()) {
      alert("请输入旅行天数")
      return
    }
    
    if (!formData.travelers.trim()) {
      alert("请输入出行人数")
      return
    }
    
    // 转换为数字类型存储
    const submitData = {
      ...formData,
      days: parseInt(formData.days) || 2,
      travelers: parseInt(formData.travelers) || 2
    }
    
    localStorage.setItem('travelPlan', JSON.stringify(submitData))
    router.push('/plan')
  }

  const loadPreset = (preset: typeof presetExamples[0]) => {
    setFormData({
      ...formData,
      destination: preset.destination,
      days: String(preset.days),
      budget: preset.budget,
      preferences: preset.preferences
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* 移动端优化的顶部导航栏 */}
      <div className="sticky top-0 z-40 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <Plane className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
              <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-orange-500 to-blue-600 bg-clip-text text-transparent">
                TravelPlanGPT
              </h1>
            </div>

            {/* 桌面端用户菜单 */}
            <div className="hidden md:flex items-center gap-2">
              {user ? (
                <>
                  <Button variant="ghost" size="sm" className="gap-2 text-sm">
                    <User className="w-4 h-4" />
                    <span className="hidden lg:inline">{user.email}</span>
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => router.push('/history')} className="gap-2">
                    <History className="w-4 h-4" />
                    <span className="hidden lg:inline">历史记录</span>
                  </Button>
                  <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2">
                    <LogOut className="w-4 h-4" />
                    <span className="hidden lg:inline">退出</span>
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="ghost" size="sm" onClick={() => router.push('/login')} className="gap-2">
                    <LogIn className="w-4 h-4" />
                    <span className="hidden lg:inline">登录</span>
                  </Button>
                  <Button size="sm" onClick={() => router.push('/register')}>
                    注册
                  </Button>
                </>
              )}
            </div>

            {/* 移动端菜单按钮 */}
            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="p-2"
              >
                {showMobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* 移动端下拉菜单 */}
          {showMobileMenu && (
            <div className="md:hidden mt-3 pb-3 border-t border-gray-200 dark:border-gray-800 pt-3 space-y-2">
              {user ? (
                <>
                  <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
                    <User className="w-4 h-4" />
                    {user.email}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => router.push('/history')} className="w-full justify-start gap-2">
                    <History className="w-4 h-4" />
                    历史记录
                  </Button>
                  <Button variant="ghost" size="sm" onClick={handleLogout} className="w-full justify-start gap-2 text-red-600 dark:text-red-400">
                    <LogOut className="w-4 h-4" />
                    退出登录
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="ghost" size="sm" onClick={() => router.push('/login')} className="w-full justify-start gap-2">
                    <LogIn className="w-4 h-4" />
                    登录
                  </Button>
                  <Button size="sm" onClick={() => router.push('/register')} className="w-full">
                    注册账号
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="container mx-auto px-4 py-4 sm:py-6 lg:py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8 lg:mb-12">
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-3 sm:mb-4">
            <Plane className="w-8 h-8 sm:w-12 sm:h-12 text-primary animate-pulse" />
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-orange-500 to-blue-600 bg-clip-text text-transparent">
              TravelPlanGPT
            </h1>
            <Sparkles className="w-8 h-8 sm:w-12 sm:h-12 text-blue-500 animate-pulse" />
          </div>
          <p className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-2xl mx-auto px-4">
            输入你的旅行需求，AI将为你生成一份完美的周末行程！🚀
          </p>
          {user && (
            <p className="text-xs sm:text-sm text-muted-foreground mt-2">
              💾 登录状态下生成的行程将自动保存到历史记录
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {/* 主表单 - 移动端和桌面端都优先显示 */}
          <div className="lg:col-span-2 order-1 lg:order-1">
            <Card className="shadow-xl border-2">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl sm:text-2xl">创建你的旅行计划</CardTitle>
                <CardDescription className="text-sm sm:text-base">填写下方信息，让AI为你规划专属行程</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
                  {/* 行程名称 */}
                  <div className="space-y-2">
                    <Label htmlFor="agentName" className="text-sm sm:text-base">行程名称（可选）</Label>
                    <Input
                      id="agentName"
                      placeholder="例如：我的周末旅行"
                      value={formData.agentName}
                      onChange={(e) => setFormData({...formData, agentName: e.target.value})}
                      className="text-sm sm:text-base"
                    />
                  </div>

                  {/* 目的地 */}
                  <div className="space-y-2">
                    <Label htmlFor="destination" className="flex items-center gap-2 text-sm sm:text-base">
                      <MapPin className="w-4 h-4" />
                      目的地城市 <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="destination"
                      placeholder="例如：上海、东京、巴黎"
                      value={formData.destination}
                      onChange={(e) => setFormData({...formData, destination: e.target.value})}
                      className="text-sm sm:text-base"
                      required
                    />
                  </div>

                  {/* 天数和人数 */}
                  <div className="grid grid-cols-2 gap-3 sm:gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="days" className="flex items-center gap-2 text-sm sm:text-base">
                        <Calendar className="w-4 h-4" />
                        旅行天数
                      </Label>
                      <Input
                        id="days"
                        type="number"
                        min="1"
                        max="5"
                        value={formData.days}
                        onChange={(e) => setFormData({...formData, days: e.target.value})}
                        className="text-sm sm:text-base"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="travelers" className="flex items-center gap-2 text-sm sm:text-base">
                        <Users className="w-4 h-4" />
                        出行人数
                      </Label>
                      <Input
                        id="travelers"
                        type="number"
                        min="1"
                        value={formData.travelers}
                        onChange={(e) => setFormData({...formData, travelers: e.target.value})}
                        className="text-sm sm:text-base"
                      />
                    </div>
                  </div>

                  {/* 预算 */}
                  <div className="space-y-2">
                    <Label htmlFor="budget" className="flex items-center gap-2 text-sm sm:text-base">
                      <DollarSign className="w-4 h-4" />
                      预算范围
                    </Label>
                    <Input
                      id="budget"
                      placeholder="例如：2000-5000元"
                      value={formData.budget}
                      onChange={(e) => setFormData({...formData, budget: e.target.value})}
                      className="text-sm sm:text-base"
                    />
                  </div>

                  {/* 偏好标签 */}
                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">偏好标签（多选）</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                      {preferenceOptions.map((pref) => {
                        const IconComponent = pref.icon === "Utensils" ? Utensils :
                          pref.icon === "Mountain" ? Mountain :
                          pref.icon === "ShoppingBag" ? ShoppingBag :
                          pref.icon === "Theater" ? Theater :
                          pref.icon === "Leaf" ? Leaf :
                          pref.icon === "Compass" ? Compass : Baby;
                        return (
                          <Button
                            key={pref.value}
                            type="button"
                            variant={formData.preferences.includes(pref.value) ? "default" : "outline"}
                            className="justify-start text-xs sm:text-sm h-9 sm:h-10"
                            onClick={() => handlePreferenceToggle(pref.value)}
                          >
                            <IconComponent className="w-4 h-4 mr-1 sm:mr-2" />
                            {pref.label}
                          </Button>
                        );
                      })}
                    </div>
                  </div>

                  {/* 额外要求 */}
                  <div className="space-y-2">
                    <Label htmlFor="extra" className="text-sm sm:text-base">额外要求（可选）</Label>
                    <Textarea
                      id="extra"
                      placeholder="例如：避免热门景点、多安排拍照点、素食友好..."
                      value={formData.extraRequirements}
                      onChange={(e) => setFormData({...formData, extraRequirements: e.target.value})}
                      rows={3}
                      className="text-sm sm:text-base resize-none"
                    />
                  </div>

                  {/* 提交按钮 */}
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full text-base sm:text-lg font-semibold shadow-lg hover:shadow-xl transition-all h-11 sm:h-12"
                    disabled={!formData.destination}
                  >
                    <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                    生成行程
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* 预设示例侧边栏 - 移动端横向滚动，桌面端垂直布局 */}
          <div className="order-2 lg:order-2">
            {/* 移动端：横向滚动卡片 - 放在表单下方 */}
            <div className="lg:hidden mt-4">
              <h3 className="text-base font-semibold px-2 mb-3">快速开始 ✨</h3>
              <div className="flex gap-3 overflow-x-auto pb-2 px-2 -mx-2 scrollbar-hide">
                {presetExamples.map((preset, index) => {
                  const IconComponent = preset.icon === "utensils" ? Utensils :
                    preset.icon === "mountain" ? Mountain : Landmark;
                  return (
                    <Card
                      key={index}
                      className="cursor-pointer hover:shadow-lg transition-all active:scale-[0.98] flex-shrink-0 w-[280px]"
                      onClick={() => loadPreset(preset)}
                    >
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base flex items-center gap-2">
                          <IconComponent className="w-5 h-5 text-primary" />
                          {preset.title}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="text-xs text-muted-foreground space-y-1">
                        <p className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {preset.destination}</p>
                        <p className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {preset.days}天</p>
                        <p className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> {preset.budget}</p>
                        <div className="flex gap-1 flex-wrap mt-2">
                          {preset.preferences.map(p => (
                            <span key={p} className="px-2 py-0.5 bg-primary/10 rounded text-xs">
                              {p}
                            </span>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
            
            {/* 桌面端：垂直卡片布局 */}
            <div className="hidden lg:block space-y-3 sm:space-y-4">
              <h3 className="text-base sm:text-lg font-semibold px-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                快速开始
              </h3>
              {presetExamples.map((preset, index) => {
                const IconComponent = preset.icon === "utensils" ? Utensils :
                  preset.icon === "mountain" ? Mountain : Landmark;
                return (
                  <Card
                    key={index}
                    className="cursor-pointer hover:shadow-lg transition-all hover:scale-[1.02] active:scale-[0.98]"
                    onClick={() => loadPreset(preset)}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base sm:text-lg flex items-center gap-2">
                        <IconComponent className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
                        {preset.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs sm:text-sm text-muted-foreground space-y-1">
                      <p className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {preset.destination}</p>
                      <p className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {preset.days}天</p>
                      <p className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> {preset.budget}</p>
                      <div className="flex gap-1 flex-wrap mt-2">
                        {preset.preferences.map(p => (
                          <span key={p} className="px-2 py-0.5 bg-primary/10 rounded text-xs">
                            {p}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
