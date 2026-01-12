"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plane, Loader2, Mail, Lock, CheckCircle2, Eye, EyeOff, UserPlus, AlertCircle } from "lucide-react"

export default function RegisterPage() {
  const router = useRouter()
  const { register, sendVerificationCode, verifyCode } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [verificationCode, setVerificationCode] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sendingCode, setSendingCode] = useState(false)
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [resendTimer, setResendTimer] = useState(0)
  const [showPasswords, setShowPasswords] = useState(false)

  // 倒计时定时器
  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendTimer])

  // 发送验证码
  const handleSendVerificationCode = useCallback(async (e?: React.MouseEvent) => {
    e?.preventDefault()
    e?.stopPropagation()
    
    if (!email) {
      setSuccessMessage("") // 先清除成功消息
      setError("请先输入邮箱")
      return
    }

    if (error.includes("邮箱已注册") || error.includes("Email already registered")) {
      return
    }

    setSendingCode(true)
    setSuccessMessage("") // 先清除成功消息
    setError("") // 然后清除错误消息
    
    try {
      await sendVerificationCode(email)
      setError("") // 确保错误消息已清除
      setSuccessMessage("验证码已发送到您的邮箱，请查收")
      setResendTimer(60) // 60秒后可重新发送
    } catch (err: any) {
      setSuccessMessage("") // 确保成功消息已清除
      setError(err.message || "发送验证码失败")
    } finally {
      setSendingCode(false)
    }
  }, [email, error, sendVerificationCode])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccessMessage("")

    // 验证密码
    if (password.length < 6) {
      setError("密码长度至少6位")
      return
    }

    if (password !== confirmPassword) {
      setError("两次输入的密码不一致")
      return
    }

    if (!verificationCode) {
      setError("请输入验证码")
      return
    }

    setIsLoading(true)

    try {
      // 先验证验证码
      await verifyCode(email, verificationCode)
      
      // 然后注册用户
      await register(email, password)
      
      // 延迟跳转以确保状态更新完成
      setTimeout(() => {
        router.push("/")
      }, 100)
    } catch (err: any) {
      if (err.message?.includes("验证码") || err.message?.includes("无效") || err.message?.includes("过期")) {
        setError("验证码无效或已过期")
      } else {
        setError(err.message || "注册失败，请稍后重试")
      }
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="bg-gradient-to-r from-orange-500 to-blue-600 p-3 rounded-full">
              <UserPlus className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl sm:text-3xl font-bold">创建账号</CardTitle>
          <CardDescription className="text-sm sm:text-base">注册 TravelPlanGPT，保存您的旅行计划</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div key="error" className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {successMessage && (
              <div key="success" className="flex items-start gap-2 p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-green-600 dark:text-green-400">{successMessage}</p>
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">邮箱地址</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  required
                  disabled={isLoading || sendingCode}
                />
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleSendVerificationCode}
                disabled={sendingCode || resendTimer > 0 || (!!error && (error.includes("邮箱已注册") || error.includes("Email already registered")))}
                className="w-full h-9"
              >
                {sendingCode ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                    发送中...
                  </>
                ) : resendTimer > 0 ? (
                  `重新发送 (${resendTimer}s)`
                ) : (
                  "发送验证码"
                )}
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="verificationCode">验证码</Label>
              <Input
                id="verificationCode"
                type="text"
                placeholder="输入验证码"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                className="text-center text-lg tracking-widest"
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPasswords ? "text" : "password"}
                  placeholder="至少6位密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10"
                  required
                  disabled={isLoading}
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  disabled={isLoading}
                >
                  {showPasswords ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">确认密码</Label>
              <div className="relative">
                <CheckCircle2 className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                <Input
                  id="confirmPassword"
                  type={showPasswords ? "text" : "password"}
                  placeholder="再次输入密码"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-10 pr-10"
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  disabled={isLoading}
                >
                  {showPasswords ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  注册中...
                </>
              ) : (
                "注册"
              )}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              已有账号？{" "}
              <Link href="/login" className="text-primary hover:underline font-medium">
                立即登录
              </Link>
            </div>

            <div className="text-center">
              <Link href="/" className="text-sm text-muted-foreground hover:underline">
                跳过注册，直接使用
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
