import { useState, useEffect, useRef } from 'react'
import { nutritionApi } from '../api/nutrition'
import { useAuthStore } from '../stores/authStore'
import { showToast } from '../components/common/Toast'
import { getHealthGoalLabel } from '../utils/format'

type GoalType = 'lose_fat' | 'build_muscle' | 'control_sugar'

const goalOptions: { value: GoalType; label: string; icon: string }[] = [
  { value: 'lose_fat', label: '减脂', icon: '🔥' },
  { value: 'build_muscle', label: '增肌', icon: '💪' },
  { value: 'control_sugar', label: '控糖', icon: '🍬' },
]

export function MealPlanner() {
  const { user } = useAuthStore()
  const [goal, setGoal] = useState<GoalType>(
    (user?.health_goal as GoalType) || 'lose_fat',
  )
  const [loading, setLoading] = useState(false)
  const [text, setText] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  const handleGenerate = async () => {
    setText('')
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/nutrition/recommend?health_goal=${goal}&target_calories=${user?.daily_calorie_target || 2000}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          Accept: 'text/event-stream',
        },
      })

      if (!response.ok) throw new Error('请求失败')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error('无法读取流')

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        setText((prev) => prev + decoder.decode(value, { stream: true }))
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : '生成失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [text])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">🍽️ AI 食谱推荐</h1>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="font-semibold text-gray-800 mb-4">🤖 根据你的健康目标生成个性化食谱</h2>

        <div className="flex gap-3 mb-6">
          {goalOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setGoal(opt.value)}
              className={`px-5 py-2.5 rounded-full text-sm font-medium border transition-colors ${
                goal === opt.value
                  ? 'bg-primary-50 text-primary-700 border-primary-300'
                  : 'text-gray-500 border-gray-200 hover:border-gray-300'
              }`}
            >
              {opt.icon} {opt.label}
            </button>
          ))}
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 text-lg"
        >
          {loading ? '⏳ AI 正在生成食谱...' : '✨ 生成今日食谱'}
        </button>

        {text && (
          <div
            ref={containerRef}
            className="mt-6 p-6 bg-gradient-to-br from-primary-50 via-white to-primary-100 rounded-xl border border-gray-100 max-h-96 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed text-gray-700"
          >
            {text}
          </div>
        )}
      </div>
    </div>
  )
}
