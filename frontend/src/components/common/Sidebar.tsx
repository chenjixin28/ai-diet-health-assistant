import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const navItems = [
  { path: '/dashboard', label: '仪表板', icon: '📊' },
  { path: '/recognition', label: '食物识别', icon: '📸' },
  { path: '/nutrition', label: '营养分析', icon: '📋' },
  { path: '/meal-planner', label: '食谱推荐', icon: '🍽️' },
]

export function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-60 bg-white border-r border-gray-200 h-screen flex flex-col shrink-0">
      <div className="p-6 border-b border-gray-100">
        <Link to="/dashboard" className="flex items-center gap-2 text-lg font-bold text-primary-700 no-underline">
          <span className="text-2xl">🥗</span>
          饮食健康助手
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-700 hover:bg-primary-50 hover:text-primary-700 transition-colors no-underline text-sm"
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <div className="text-sm text-gray-500 mb-2 truncate">👤 {user?.username}</div>
        <button
          onClick={handleLogout}
          className="w-full py-2 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          退出登录
        </button>
      </div>
    </aside>
  )
}
