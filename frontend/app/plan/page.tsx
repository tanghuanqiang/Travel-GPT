"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Pause, Play, StopCircle, CheckCircle2, ArrowRight } from "lucide-react"
import axios from "axios"

interface LogEntry {
  step: string
  status: "running" | "completed" | "error"
  message: string
  timestamp: string
}

interface ItineraryData {
  overview: {
    totalBudget: number
    budgetBreakdown: {
      category: string
      amount: number
    }[]
  }
  dailyPlans: {
    day: number
    title: string
    activities: {
      time: string
      title: string
      description: string
      duration: string
      cost: number
      address: string
      reason: string
      images?: string[]
    }[]
  }[]
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

export default function PlanPage() {
  const router = useRouter()
  const { token } = useAuth()
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isRunning, setIsRunning] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  const [progress, setProgress] = useState(0)
  const [planData, setPlanData] = useState<ItineraryData | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // 防止 React StrictMode 导致的重复请求
  const hasStartedRef = useRef(false)

  useEffect(() => {
    // 防止重复执行
    if (hasStartedRef.current) {
      return
    }
    hasStartedRef.current = true
    
    const savedData = localStorage.getItem('travelPlan')
    if (!savedData) {
      router.push('/')
      return
    }

    // 补全所有后端需要的字段
    const defaultRequest = {
      agentName: "我的周末旅行",
      destination: "",
      days: 2,
      budget: "",
      travelers: 2,
      preferences: [],
      extraRequirements: ""
    };
    const formData = { ...defaultRequest, ...JSON.parse(savedData) };
    startPlanning(formData)
  }, [])

  const startPlanning = async (formData: any) => {
    try {
      // 模拟Agent思考过程
      const steps = [
        { step: "init", message: `正在初始化旅行规划：${formData.destination}` },
        { step: "search", message: "搜索热门景点和隐藏宝石..." },
        { step: "food", message: "寻找当地美食和特色餐厅..." },
        { step: "budget", message: "计算预算分配..." },
        { step: "route", message: "优化行程路线..." },
        { step: "tips", message: "收集实用旅行建议..." },
        { step: "finalize", message: "生成最终行程计划..." }
      ]

      for (let i = 0; i < steps.length; i++) {
        if (!isPaused) {
          setLogs(prev => [...prev, {
            ...steps[i],
            status: "running",
            timestamp: new Date().toLocaleTimeString()
          }])
          setProgress((i + 1) / steps.length * 100)
          
          // 模拟延迟
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          setLogs(prev => prev.map((log, idx) => 
            idx === prev.length - 1 ? { ...log, status: "completed" } : log
          ))
        }
      }

      // 实际调用后端API
      const headers: any = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await axios.post('http://localhost:8000/api/generate-plan', formData, { headers })
      setPlanData(response.data)
      setIsRunning(false)
      
      // 保存结果并跳转
      localStorage.setItem('itinerary', JSON.stringify(response.data))
      setTimeout(() => {
        router.push('/result')
      }, 1000)

    } catch (err) {
      console.error('Planning error:', err)
      setError('生成行程时出错，请重试')
      setIsRunning(false)
    }
  }

  const handlePause = () => {
    setIsPaused(!isPaused)
  }

  const handleStop = () => {
    setIsRunning(false)
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <span className="text-4xl">✈️</span>
            AI旅行规划中...
          </h1>
          <p className="text-gray-300">请稍候，Agent正在为你生成完美行程</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Log Panel */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-800/50 backdrop-blur border-gray-700 min-h-[500px]">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Loader2 className={`w-5 h-5 ${isRunning ? 'animate-spin' : ''}`} />
                    Agent思考日志
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handlePause}
                      disabled={!isRunning}
                    >
                      {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleStop}
                    >
                      <StopCircle className="w-4 h-4" />
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {logs.map((log, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 bg-gray-700/30 rounded-lg animate-fadeIn"
                  >
                    {log.status === "completed" ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    ) : log.status === "running" ? (
                      <Loader2 className="w-5 h-5 text-blue-400 animate-spin flex-shrink-0 mt-0.5" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-gray-500 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{log.message}</p>
                      <p className="text-xs text-gray-400 mt-1">{log.timestamp}</p>
                    </div>
                  </div>
                ))}
                
                {error && (
                  <div className="p-4 bg-red-500/20 border border-red-500 rounded-lg">
                    <p className="text-red-200">{error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Progress Panel */}
          <div className="space-y-6">
            {/* Progress Bar */}
            <Card className="bg-gray-800/50 backdrop-blur border-gray-700">
              <CardHeader>
                <CardTitle className="text-lg">整体进度</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>完成度</span>
                    <span className="font-bold">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Status Info */}
            <Card className="bg-gray-800/50 backdrop-blur border-gray-700">
              <CardHeader>
                <CardTitle className="text-lg">当前状态</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">运行状态</span>
                  <span className={isRunning ? "text-green-400" : "text-gray-400"}>
                    {isRunning ? "运行中" : "已停止"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">已完成步骤</span>
                  <span className="text-blue-400">{logs.filter(l => l.status === "completed").length} / {logs.length}</span>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="bg-gradient-to-br from-orange-500/20 to-purple-500/20 backdrop-blur border-orange-500/30">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>💡</span>
                  小提示
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p>• AI正在分析数百个景点和餐厅</p>
                <p>• 会为你找到隐藏的本地宝藏</p>
                <p>• 预算将被智能分配优化</p>
                <p>• 路线已按地理位置优化</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
