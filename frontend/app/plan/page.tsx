"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Pause, Play, StopCircle, CheckCircle2, ArrowRight } from "lucide-react"
import axios from "axios"
import { api } from "@/lib/api"

interface LogEntry {
  step: string
  status: "running" | "completed" | "error"
  message: string
  timestamp: string
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
  const [isFinalizing, setIsFinalizing] = useState(false) // 是否正在最终归纳总结
  const [finalizingTipIndex, setFinalizingTipIndex] = useState(0) // 当前显示的提示文字索引
  
  // 最终归纳阶段的提示文字
  const finalizingTips = [
    "正在整理行程细节，确保每一个活动都精彩...",
    "优化时间安排，让您的旅途更加顺畅...",
    "检查预算分配，确保物超所值...",
    "完善实用建议，让您的旅行更轻松...",
    "最后检查行程路线，确保行程合理...",
    "为您呈现最完美的旅行计划..."
  ]
  
  // 防止 React StrictMode 导致的重复请求
  const hasStartedRef = useRef(false)
  // 存储当前任务的ID，确保并发安全
  const currentTaskIdRef = useRef<string | null>(null)
  // 用于取消轮询的标记
  const isCancelledRef = useRef(false)
  
  // 当进入最终归纳阶段时，每2秒切换提示文字
  useEffect(() => {
    if (!isFinalizing) return
    
    const interval = setInterval(() => {
      setFinalizingTipIndex((prev) => (prev + 1) % finalizingTips.length)
    }, 2000)
    
    return () => clearInterval(interval)
  }, [isFinalizing, finalizingTips.length])

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
      // 规划步骤
      const steps = [
        { step: "init", message: `了解您的${formData.destination}旅行需求` },
        { step: "search", message: `为您寻找${formData.destination}的热门景点和特色体验` },
        { step: "food", message: `发现${formData.destination}当地美食和推荐餐厅` },
        { step: "budget", message: "合理规划预算，确保每一分钱都花得值" },
        { step: "route", message: "优化行程路线，让您的旅途更顺畅" },
        { step: "tips", message: "整理实用建议和小贴士" },
        { step: "finalize", message: "完善行程细节，为您呈现完美计划" }
      ]

      // 初始步骤进度范围：0-35%
      const initialProgressMax = 35
      
      for (let i = 0; i < steps.length; i++) {
        if (!isPaused) {
          setLogs(prev => [...prev, {
            ...steps[i],
            status: "running",
            timestamp: new Date().toLocaleTimeString()
          }])
          // 初始步骤占总进度的35%
          setProgress(((i + 1) / steps.length) * initialProgressMax)
          
          // 模拟延迟
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          setLogs(prev => prev.map((log, idx) => 
            idx === prev.length - 1 ? { ...log, status: "completed" } : log
          ))
        }
      }

      // 所有步骤完成，进入最终归纳阶段
      setIsFinalizing(true)
      // 初始步骤完成，进度设置为35%
      setProgress(initialProgressMax)
      
      // 调用后端API创建任务
      const headers: any = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18890'
      
      // 重置取消标记
      isCancelledRef.current = false
      
      // 创建任务，获取task_id
      const taskResponse = await axios.post(`${apiUrl}/api/generate-plan`, formData, { headers })
      const taskId = taskResponse.data.task_id
      
      // 存储当前任务ID，确保并发安全
      currentTaskIdRef.current = taskId
      
      console.log('任务已创建，task_id:', taskId)
      
      // 轮询任务状态
      const pollTaskStatus = async (): Promise<any> => {
        const maxAttempts = 150 // 最多轮询5分钟（每2秒一次，5分钟=300秒/2=150次）
        let attempts = 0
        
        // 进度范围：35% (初始完成) -> 95% (轮询中) -> 100% (完成)
        const progressStart = 35  // 轮询开始时的进度
        const progressEnd = 95    // 轮询结束时的进度（完成前）
        
        while (attempts < maxAttempts) {
          // 检查是否已取消（用户可能离开了页面或开始了新任务）
          if (isCancelledRef.current) {
            throw new Error('任务已取消')
          }
          
          // 验证当前任务ID是否仍然有效（防止并发问题）
          if (currentTaskIdRef.current !== taskId) {
            throw new Error('检测到新任务，已取消当前任务')
          }
          
          // 更新进度：从35%逐渐增加到95%
          const progressIncrement = (progressEnd - progressStart) / maxAttempts
          const currentProgress = Math.min(progressStart + (attempts * progressIncrement), progressEnd)
          setProgress(currentProgress)
          
          try {
            const statusResponse = await axios.get(`${apiUrl}/api/tasks/${taskId}`, { headers })
            const taskStatus = statusResponse.data
            
            // 再次验证任务ID（双重检查）
            if (currentTaskIdRef.current !== taskId) {
              throw new Error('检测到新任务，已取消当前任务')
            }
            
            console.log(`任务状态 (${attempts + 1}/${maxAttempts}):`, taskStatus.status, 'task_id:', taskId, `进度: ${currentProgress.toFixed(1)}%`)
            
            if (taskStatus.status === 'completed') {
              // 验证返回的任务ID是否匹配（确保是当前用户的任务）
              if (taskStatus.task_id !== taskId) {
                throw new Error('任务ID不匹配，可能存在并发问题')
              }
              // 任务完成，进度设置为100%
              setProgress(100)
              // 任务完成，返回结果
              return taskStatus.result
            } else if (taskStatus.status === 'failed') {
              // 任务失败
              throw new Error(taskStatus.error_message || '任务处理失败')
            } else {
              // 任务还在处理中，继续等待
              await new Promise(resolve => setTimeout(resolve, 2000)) // 等待2秒
              attempts++
            }
          } catch (err: any) {
            // 如果已取消，直接抛出
            if (isCancelledRef.current || currentTaskIdRef.current !== taskId) {
              throw new Error('任务已取消')
            }
            
            if (err.response?.status === 404) {
              throw new Error('任务不存在')
            }
            // 网络错误，继续重试
            await new Promise(resolve => setTimeout(resolve, 2000)) // 等待2秒
            attempts++
          }
        }
        
        throw new Error('任务处理超时，请稍后重试')
      }
      
      // 开始轮询
      const result = await pollTaskStatus()
      
      // 再次验证任务ID（确保结果属于当前任务）
      if (currentTaskIdRef.current !== taskId) {
        throw new Error('任务ID不匹配，结果可能不属于当前任务')
      }
      
      setPlanData(result)
      setIsRunning(false)
      setIsFinalizing(false)
      
      // 保存结果到localStorage（向后兼容）
      localStorage.setItem('itinerary', JSON.stringify(result))
      
      // 如果是游客用户，创建临时分享链接并跳转到唯一URL
      if (!token) {
        try {
          // 从localStorage获取原始请求参数，包含destination和days
          const travelPlan = localStorage.getItem('travelPlan')
          let shareDataToSend = { ...result }
          
          if (travelPlan) {
            try {
              const planData = JSON.parse(travelPlan)
              shareDataToSend.destination = planData.destination || ""
              shareDataToSend.days = planData.days || result.dailyPlans?.length || 2
            } catch (e) {
              shareDataToSend.destination = ""
              shareDataToSend.days = result.dailyPlans?.length || 2
            }
          } else {
            shareDataToSend.destination = ""
            shareDataToSend.days = result.dailyPlans?.length || 2
          }
          
          // 创建临时分享链接
          const shareResponse = await axios.post(`${apiUrl}/api/share/temporary`, {
            itinerary_data: shareDataToSend,
            expires_days: 7
          })
          
          // 跳转到带token的唯一URL
          setTimeout(() => {
            router.push(`/result?token=${shareResponse.data.share_token}`)
          }, 1000)
        } catch (shareErr: any) {
          console.error('创建分享链接失败:', shareErr)
          // 如果创建分享链接失败，仍然跳转到普通result页面（向后兼容）
          setTimeout(() => {
            router.push('/result')
          }, 1000)
        }
      } else {
        // 登录用户：如果有itinerary_id，跳转到带id的URL；否则跳转到普通result
        setTimeout(() => {
          // 登录用户的行程已保存到数据库，可以通过历史记录访问
          router.push('/result')
        }, 1000)
      }

    } catch (err: any) {
      console.error('Planning error:', err)
      setError(err.message || '生成行程时出错，请重试')
      setIsRunning(false)
      setIsFinalizing(false)
    }
  }

  const handlePause = () => {
    setIsPaused(!isPaused)
  }

  const handleStop = () => {
    // 取消当前任务
    isCancelledRef.current = true
    currentTaskIdRef.current = null
    setIsRunning(false)
    router.push('/')
  }
  
  // 组件卸载时清理
  useEffect(() => {
    return () => {
      // 组件卸载时取消任务
      isCancelledRef.current = true
      currentTaskIdRef.current = null
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-3 text-gray-900 dark:text-white">
            正在为您规划行程
          </h1>
          <p className="text-gray-600 dark:text-gray-300 text-sm sm:text-base">稍等片刻，我们正在为您精心准备一份完美的旅行计划</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Log Panel */}
          <div className="lg:col-span-2">
            <Card className="bg-white/95 dark:bg-gray-800/95 backdrop-blur border-gray-200 dark:border-gray-700 min-h-[500px]">
              <CardHeader className="border-b border-gray-200 dark:border-gray-700">
                <CardTitle className="flex items-center justify-between text-gray-900 dark:text-white">
                  <span className="text-lg sm:text-xl font-semibold">
                    规划进度
                  </span>
                  {isRunning && (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handlePause}
                        className="hidden sm:flex"
                      >
                        {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleStop}
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      >
                        <StopCircle className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 p-4 sm:p-6">
                {logs.map((log, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 transition-all duration-200 animate-fadeIn"
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {log.status === "completed" ? (
                        <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                          <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                        </div>
                      ) : log.status === "running" ? (
                        <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                          <Loader2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
                        </div>
                      ) : (
                        <div className="w-6 h-6 rounded-full border-2 border-gray-300 dark:border-gray-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-gray-100">{log.message}</p>
                      {log.status === "running" && (
                        <div className="mt-2 h-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {/* 最终归纳阶段的额外提示 */}
                {isFinalizing && progress >= 100 && (
                  <div className="flex items-start gap-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 animate-fadeIn">
                    <div className="flex-shrink-0 mt-0.5">
                      <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                        <Loader2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm sm:text-base font-medium text-blue-900 dark:text-blue-100 mb-2">
                        正在归纳总结
                      </p>
                      <p className="text-sm text-blue-700 dark:text-blue-300 transition-opacity duration-300">
                        {finalizingTips[finalizingTipIndex]}
                      </p>
                      <div className="mt-3 h-1.5 w-full bg-blue-200 dark:bg-blue-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '100%' }} />
                      </div>
                    </div>
                  </div>
                )}
                
                {error && (
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Progress Panel */}
          <div className="space-y-6">
            {/* Progress Bar */}
            <Card className="bg-white/95 dark:bg-gray-800/95 backdrop-blur border-gray-200 dark:border-gray-700">
              <CardHeader className="border-b border-gray-200 dark:border-gray-700">
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">整体进度</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">完成度</span>
                    <span className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-orange-500 to-blue-500 transition-all duration-500 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    已完成 {logs.filter(l => l.status === "completed").length} / {logs.length} 个步骤
                  </div>
                  
                  {/* 最终归纳阶段提示 */}
                  {isFinalizing && progress >= 100 && (
                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <div className="flex items-center gap-3 mb-3">
                        <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0" />
                        <span className="text-sm font-medium text-blue-900 dark:text-blue-100">正在归纳总结</span>
                      </div>
                      <p className="text-sm text-blue-700 dark:text-blue-300 transition-opacity duration-300">
                        {finalizingTips[finalizingTipIndex]}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="bg-gradient-to-br from-orange-50 to-blue-50 dark:from-orange-900/20 dark:to-blue-900/20 backdrop-blur border-orange-200 dark:border-orange-800/50">
              <CardHeader className="border-b border-orange-200/50 dark:border-orange-800/50">
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  贴心提示
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 text-sm space-y-3 text-gray-700 dark:text-gray-300">
                <p className="flex items-start gap-2">
                  <span className="text-orange-500 dark:text-orange-400 mt-0.5">•</span>
                  <span>为您精选热门景点和特色体验</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-orange-500 dark:text-orange-400 mt-0.5">•</span>
                  <span>发现当地美食和推荐餐厅</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-orange-500 dark:text-orange-400 mt-0.5">•</span>
                  <span>合理规划预算，让每一分钱都花得值</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-orange-500 dark:text-orange-400 mt-0.5">•</span>
                  <span>优化路线安排，节省旅途时间</span>
                </p>
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
