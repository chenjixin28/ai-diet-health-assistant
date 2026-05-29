import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'
import { showToast } from '../components/common/Toast'

export function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password) return
    setLoading(true)
    try {
      const { data } = await authApi.login({ username: username.trim(), password })
      if (data.success && data.data) {
        localStorage.setItem('access_token', data.data.access_token)
        const profileRes = await authApi.getMe()
        if (profileRes.data.success) {
          login(profileRes.data.data, data.data.access_token)
        } else {
          login(data.data as unknown as typeof profileRes.data.data, data.data.access_token)
        }
        showToast('登录成功', 'success')
        navigate('/dashboard')
      } else {
        showToast(data.detail || '登录失败', 'error')
      }
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : '登录失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <div className="w-full max-w-md px-8">
        <div className="text-center mb-8">
          <span className="text-5xl">🥗</span>
          <h1 className="text-2xl font-bold text-gray-900 mt-3">AI饮食健康助手</h1>
          <p className="text-gray-500 mt-1">记录每一餐，健康每一天</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 space-y-5">
          <h2 className="text-lg font-semibold text-gray-800">登录</h2>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">用户名 / 邮箱</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="请输入用户名或邮箱"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="请输入密码"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? '登录中...' : '登 录'}
          </button>

          <p className="text-center text-sm text-gray-500">
            还没有账号？
            <Link to="/register" className="text-primary-600 hover:underline ml-1">立即注册</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
