import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { showToast } from '../components/common/Toast'

export function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !email.trim() || !password) return
    if (password !== confirmPassword) {
      showToast('两次密码输入不一致', 'error')
      return
    }
    if (password.length < 6) {
      showToast('密码至少6位', 'error')
      return
    }
    setLoading(true)
    try {
      const { data } = await authApi.register({
        username: username.trim(),
        email: email.trim(),
        password,
      })
      if (data.success) {
        showToast('注册成功，请登录', 'success')
        navigate('/login')
      } else {
        showToast(data.detail || '注册失败', 'error')
      }
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : '注册失败', 'error')
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
          <p className="text-gray-500 mt-1">开始你的健康之旅</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">注册</h2>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">用户名</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="3-50位字母数字"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">邮箱</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="example@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="至少6位"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">确认密码</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-400 focus:border-transparent outline-none transition-shadow"
              placeholder="再次输入密码"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? '注册中...' : '注 册'}
          </button>

          <p className="text-center text-sm text-gray-500">
            已有账号？
            <Link to="/login" className="text-primary-600 hover:underline ml-1">去登录</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
