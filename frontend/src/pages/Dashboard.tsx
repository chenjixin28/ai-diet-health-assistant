import { useState, useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../api/auth'
import { nutritionApi } from '../api/nutrition'
import { getHealthGoalLabel, calcCaloriePercentage } from '../utils/format'
import { showToast } from '../components/common/Toast'
import type { HealthGoal } from '../types/user'

const goalOptions: { value: HealthGoal; label: string; icon: string }[] = [
  { value: 'lose_fat', label: '减脂', icon: '🔥' },
  { value: 'build_muscle', label: '增肌', icon: '💪' },
  { value: 'control_sugar', label: '控糖', icon: '🍬' },
]

export function Dashboard() {
  const { user, setUser } = useAuthStore()
  const [editing, setEditing] = useState(false)
  const [height, setHeight] = useState(user?.height?.toString() || '')
  const [weight, setWeight] = useState(user?.weight?.toString() || '')
  const [goal, setGoal] = useState<HealthGoal | ''>(user?.health_goal || '')
  const [targetWeight, setTargetWeight] = useState(user?.target_weight?.toString() || '')
  const [saving, setSaving] = useState(false)

  const [dailyCalories, setDailyCalories] = useState(0)
  const [dailyProtein, setDailyProtein] = useState(0)

  const calorieTarget = user?.daily_calorie_target || 2000
  const proteinTarget = user?.daily_protein_target || 60

  useEffect(() => {
    nutritionApi.getToday().then((res) => {
      if (res.data.success) {
        setDailyCalories(res.data.data?.total_calories || 0)
        setDailyProtein(res.data.data?.total_protein || 0)
      }
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = {
        height: height ? parseFloat(height) : undefined,
        weight: weight ? parseFloat(weight) : undefined,
        health_goal: goal as HealthGoal | undefined,
        target_weight: targetWeight ? parseFloat(targetWeight) : undefined,
      }
      const { data } = await authApi.updateProfile(payload)
      if (data.success) {
        const { data: profile } = await authApi.getMe()
        if (profile.success) setUser(profile.data)
        showToast('档案更新成功', 'success')
        setEditing(false)
      } else {
        showToast(data.detail || '更新失败', 'error')
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : '更新失败', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">👋 你好，{user?.username}</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">今日摄入</p>
          <p className="text-3xl font-bold text-primary-600 mt-1">{dailyCalories}</p>
          <p className="text-xs text-gray-400 mt-1">/ {calorieTarget} kcal 目标</p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all"
              style={{ width: `${calcCaloriePercentage(dailyCalories, calorieTarget)}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">蛋白质</p>
          <p className="text-3xl font-bold text-primary-600 mt-1">{dailyProtein.toFixed(1)}g</p>
          <p className="text-xs text-gray-400 mt-1">/ {proteinTarget}g 目标</p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">健康目标</p>
          <p className="text-3xl mt-1">
            {goalOptions.find((g) => g.value === user?.health_goal)?.icon || '🎯'}
          </p>
          <p className="text-sm font-medium text-gray-700 mt-1">
            {user?.health_goal ? getHealthGoalLabel(user.health_goal) : '未设置'}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">📋 健康档案</h2>
          {!editing && (
            <button
              onClick={() => {
                setHeight(user?.height?.toString() || '')
                setWeight(user?.weight?.toString() || '')
                setGoal(user?.health_goal || '')
                setTargetWeight(user?.target_weight?.toString() || '')
                setEditing(true)
              }}
              className="text-sm text-primary-600 hover:underline bg-transparent border-0 cursor-pointer"
            >
              编辑
            </button>
          )}
        </div>

        {editing ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-500 mb-1">身高 (cm)</label>
                <input type="number" value={height} onChange={(e) => setHeight(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="170" />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">体重 (kg)</label>
                <input type="number" value={weight} onChange={(e) => setWeight(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="65" />
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-2">健康目标</label>
              <div className="flex gap-3">
                {goalOptions.map((opt) => (
                  <button key={opt.value} onClick={() => setGoal(opt.value)}
                    className={`flex-1 py-2.5 rounded-lg text-sm font-medium border transition-colors ${
                      goal === opt.value ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'
                    }`}
                  >{opt.icon} {opt.label}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">目标体重 (kg)</label>
              <input type="number" value={targetWeight} onChange={(e) => setTargetWeight(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="60" />
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={handleSave} disabled={saving}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 transition-colors disabled:opacity-50">
                {saving ? '保存中...' : '保存'}
              </button>
              <button onClick={() => setEditing(false)}
                className="px-6 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition-colors">取消</button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span className="text-gray-400">身高</span><p className="font-medium mt-1">{user?.height || '--'} cm</p></div>
            <div><span className="text-gray-400">体重</span><p className="font-medium mt-1">{user?.weight || '--'} kg</p></div>
            <div><span className="text-gray-400">目标</span><p className="font-medium mt-1">{user?.health_goal ? getHealthGoalLabel(user.health_goal) : '--'}</p></div>
            <div><span className="text-gray-400">目标体重</span><p className="font-medium mt-1">{user?.target_weight || '--'} kg</p></div>
          </div>
        )}
      </div>
    </div>
  )
}
