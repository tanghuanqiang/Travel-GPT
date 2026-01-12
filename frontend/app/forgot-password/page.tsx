"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Key, Loader2, Mail, Lock, AlertCircle, CheckCircle2, ArrowLeft, Eye, EyeOff } from "lucide-react"

export default function ForgotPasswordPage() {
  const router = useRouter()
  const { sendResetPasswordCode, resetPassword } = useAuth()
  const [email, setEmail] = useState("")
  const [verificationCode, setVerificationCode] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sendingCode, setSendingCode] = useState(false)
  const [resendTimer, setResendTimer] = useState(0)
  const [codeSent, setCodeSent] = useState(false)
  const [showPasswords, setShowPasswords] = useState(false)

  // 倒计时定时器
  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendTimer])

  // 发送重置密码验证码
  const handleSendResetCode = async () => {
    if (!email) {
      setError("请先输入邮箱")
      return
    }

    setSendingCode(true)
    setError("")
    
    try {
      await sendResetPasswordCode(email)
      setSuccessMessage("重置密码验证码已发送到您的邮箱，请查收")
      setResendTimer(60) // 60秒后可重新发送
      setCodeSent(true)
    } catch (err: any) {
      setError(err.message || "发送验证码失败")
    } finally {
      setSendingCode(false)
    }
  }

  // 重置密码
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccessMessage("")

    if (newPassword !== confirmPassword) {
      setError("两次输入的密码不一致")
      return
    }

    if (newPassword.length < 6) {
      setError("密码长度至少为6个字符")
      return
    }

    if (!verificationCode) {
      setError("请输入验证码")
      return
    }

    setIsLoading(true)

    try {
      await resetPassword(email, verificationCode, newPassword)
      
      setSuccessMessage("密码重置成功，正在跳转...")
      
      // 延迟跳转
      setTimeout(() => {
        router.push("/")
      }, 2000)
    } catch (err: any) {
      let errorMessage = "密码重置失败，请稍后重试"
      
      if (err.message?.includes("验证码") || err.message?.includes("无效") || err.message?.includes("过期")) {
        errorMessage = "验证码无效或已过期"
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-blue-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="bg-gradient-to-r from-orange-500 to-blue-600 p-3 rounded-full">
              <Key className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl sm:text-3xl font-bold">重置密码</CardTitle>
          <CardDescription className="text-sm sm:text-base">输入您的邮箱以重置密码</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleResetPassword} className="space-y-4">
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
                  disabled={codeSent || isLoading}
                />
              </div>
              {!codeSent && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleSendResetCode}
                  disabled={sendingCode || resendTimer > 0}
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
                    "发送重置验证码"
                  )}
                </Button>
              )}
            </div>

            {codeSent && (
              <>
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
                  <Label htmlFor="newPassword">新密码</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="newPassword"
                      type={showPasswords ? "text" : "password"}
                      placeholder="至少6个字符"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
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

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">确认新密码</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      type={showPasswords ? "text" : "password"}
                      placeholder="再次输入新密码"
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
              </>
            )}

            {error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {successMessage && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-green-600 dark:text-green-400">{successMessage}</p>
              </div>
            )}

            {codeSent && (
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    重置中...
                  </>
                ) : (
                  "重置密码"
                )}
              </Button>
            )}

            <div className="text-center">
              <Link 
                href="/login" 
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline font-medium"
              >
                <ArrowLeft className="h-3 w-3" />
                返回登录
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
