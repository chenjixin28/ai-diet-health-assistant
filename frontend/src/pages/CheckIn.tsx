import { useState, useEffect } from 'react'
import { checkinApi } from '../api/checkin'
import { showToast } from '../components/common/Toast'

interface CalendarDay {
  date: string
  day: number
  weekday: number
  checked: boolean
  is_today: boolean
  is_future: boolean
}

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  earned: boolean
}

const WEEKDAY_LABELS = ['日', '一', '二', '三', '四', '五', '六']

export function CheckIn() {
  const today = new Date()
  const [year, setYear] = useState(today.getFullYear())
  const [month, setMonth] = useState(today.getMonth() + 1)
  const [days, setDays] = useState<CalendarDay[]>([])
  const [currentStreak, setCurrentStreak] = useState(0)
  const [longestStreak, setLongestStreak] = useState(0)
  const [totalRecords, setTotalRecords] = useState(0)

  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [earnedCount, setEarnedCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [calRes, achRes] = await Promise.all([
        checkinApi.getCalendar(year, month),
        checkinApi.getAchievements(),
      ])
      if (calRes.data.success && calRes.data.data) {
        const d = calRes.data.data
        setDays(d.days || [])
        setCurrentStreak(d.current_streak || 0)
        setLongestStreak(d.longest_streak || 0)
        setTotalRecords(d.total_records || 0)
      }
      if (achRes.data.success && achRes.data.data) {
        setAchievements(achRes.data.data.achievements || [])
        setEarnedCount(achRes.data.data.earned_count || 0)
        setTotalCount(achRes.data.data.total_count || 0)
      }
    } catch {
      showToast('加载打卡数据失败', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [year, month])

  const prevMonth = () => {
    if (month === 1) { setYear(year - 1); setMonth(12) }
    else setMonth(month - 1)
  }

  const nextMonth = () => {
    const now = new Date()
    if (year === now.getFullYear() && month >= now.getMonth() + 1) return
    if (month === 12) { setYear(year + 1); setMonth(1) }
    else setMonth(month + 1)
  }

  const padDays = () => {
    if (days.length === 0) return []
    const firstWeekday = days[0].weekday
    const pads = []
    for (let i = 0; i < firstWeekday; i++) {
      pads.push(null)
    }
    return pads
  }

  const streakEmoji = currentStreak >= 30 ? '👑' : currentStreak >= 14 ? '🏅' : currentStreak >= 7 ? '⭐' : currentStreak >= 3 ? '🔥' : '🌱'

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">🏆 打卡 & 成就</h1>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors">◀</button>
              <h2 className="text-lg font-semibold text-gray-800">{year} 年 {month} 月</h2>
              <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors">▶</button>
            </div>

            <div className="grid grid-cols-7 gap-1 text-center mb-2">
              {WEEKDAY_LABELS.map((w) => (
                <div key={w} className="text-xs font-medium text-gray-400 py-2">{w}</div>
              ))}
            </div>

            <div className="grid grid-cols-7 gap-1">
              {padDays().map((_, i) => (
                <div key={`pad-${i}`} />
              ))}
              {days.map((d) => (
                <div
                  key={d.date}
                  className={`aspect-square rounded-lg flex items-center justify-center text-sm font-medium transition-all
                    ${d.is_future ? 'text-gray-300 cursor-default' : ''}
                    ${d.checked && !d.is_today ? 'bg-primary-500 text-white shadow-sm' : ''}
                    ${d.checked && d.is_today ? 'bg-primary-600 text-white shadow-md ring-2 ring-primary-300' : ''}
                    ${!d.checked && !d.is_future && !d.is_today ? 'text-gray-600 hover:bg-gray-100' : ''}
                    ${!d.checked && d.is_today ? 'bg-gray-100 text-primary-600 ring-2 ring-primary-200' : ''}
                  `}
                  title={d.checked ? '已打卡' : d.is_future ? '' : '未打卡'}
                >
                  {d.day}
                </div>
              ))}
            </div>

            <div className="flex items-center gap-4 mt-4 text-xs text-gray-400">
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-primary-500" /> 已打卡</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-gray-100 ring-2 ring-primary-200" /> 今天</span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-800 mb-3">🔥 打卡统计</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gradient-to-br from-primary-50 to-green-50 rounded-xl p-4 text-center">
                <p className="text-3xl mb-1">{streakEmoji}</p>
                <p className="text-2xl font-bold text-primary-700">{currentStreak}</p>
                <p className="text-xs text-gray-500 mt-1">当前连续</p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 text-center">
                <p className="text-3xl mb-1">🏆</p>
                <p className="text-2xl font-bold text-blue-700">{longestStreak}</p>
                <p className="text-xs text-gray-500 mt-1">最长连击</p>
              </div>
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 text-center">
                <p className="text-3xl mb-1">📝</p>
                <p className="text-2xl font-bold text-amber-700">{totalRecords}</p>
                <p className="text-xs text-gray-500 mt-1">总记录数</p>
              </div>
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-4 text-center">
                <p className="text-3xl mb-1">🎖️</p>
                <p className="text-2xl font-bold text-emerald-700">{earnedCount}/{totalCount}</p>
                <p className="text-xs text-gray-500 mt-1">已获成就</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-800 mb-3">🏅 成就徽章</h3>
            <div className="grid grid-cols-3 gap-3">
              {achievements.map((ach) => (
                <div
                  key={ach.id}
                  className={`rounded-xl p-3 text-center border transition-all ${
                    ach.earned
                      ? 'bg-gradient-to-b from-yellow-50 to-amber-50 border-amber-200 shadow-sm'
                      : 'bg-gray-50 border-gray-200 opacity-50 grayscale'
                  }`}
                >
                  <p className="text-2xl mb-1">{ach.icon}</p>
                  <p className={`text-xs font-medium ${ach.earned ? 'text-gray-800' : 'text-gray-400'}`}>
                    {ach.name}
                  </p>
                  <p className="text-[10px] text-gray-400 mt-0.5 leading-tight">{ach.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
