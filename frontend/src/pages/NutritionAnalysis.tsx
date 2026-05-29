import { useState, useEffect } from 'react'
import { Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { nutritionApi } from '../api/nutrition'
import { foodApi } from '../api/foods'
import { showToast } from '../components/common/Toast'
import type { NutritionSummary } from '../types/nutrition'
import type { FoodRecord as FoodRecordType } from '../types/food'
import { formatCalories, formatGram, getMealTypeLabel } from '../utils/format'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

export function NutritionAnalysis() {
  const [summary, setSummary] = useState<NutritionSummary[]>([])
  const [todayCal, setTodayCal] = useState(0)
  const [todayProtein, setTodayProtein] = useState(0)
  const [todayFat, setTodayFat] = useState(0)
  const [todayCarb, setTodayCarb] = useState(0)
  const [mealCount, setMealCount] = useState(0)
  const [records, setRecords] = useState<FoodRecordType[]>([])
  const [days, setDays] = useState(7)

  const fetchData = async () => {
    try {
      const [summaryRes, todayRes, recordsRes] = await Promise.all([
        nutritionApi.getSummary(days),
        nutritionApi.getToday(),
        foodApi.getRecords(),
      ])
      if (summaryRes.data.success) setSummary(summaryRes.data.data?.summary || [])
      if (todayRes.data.success) {
        const d = todayRes.data.data
        setTodayCal(d?.total_calories || 0)
        setTodayProtein(d?.total_protein || 0)
        setTodayFat(d?.total_fat || 0)
        setTodayCarb(d?.total_carbohydrates || 0)
        setMealCount(d?.meal_count || 0)
      }
      if (recordsRes.data.success) setRecords(recordsRes.data.data?.records || [])
    } catch (err) {
      showToast('获取营养数据失败', 'error')
    }
  }

  useEffect(() => {
    fetchData()
  }, [days])

  const barData = {
    labels: summary.map((s) => s.date.slice(5)),
    datasets: [
      {
        label: '热量 (kcal)',
        data: summary.map((s) => s.total_calories),
        backgroundColor: '#22c55e',
        borderRadius: 6,
      },
    ],
  }

  const doughnutData = {
    labels: ['碳水化合物', '蛋白质', '脂肪'],
    datasets: [
      {
        data: [todayCarb, todayProtein, todayFat],
        backgroundColor: ['#facc15', '#3b82f6', '#f97316'],
        borderWidth: 0,
      },
    ],
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">📋 营养分析</h1>

      <div className="flex gap-3">
        {[7, 14, 30].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
              days === d
                ? 'bg-primary-50 text-primary-700 border-primary-300'
                : 'text-gray-500 border-gray-200 hover:border-gray-300'
            }`}
          >
            近 {d} 天
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="font-semibold text-gray-800 mb-4">📊 热量摄入趋势</h2>
        {summary.length > 0 ? (
          <div className="h-64">
            <Bar
              data={barData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                  x: { grid: { display: false } },
                },
              }}
            />
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-400">
            暂无数据，去"食物识别"记录今天吃了什么吧
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">🥩 今日宏量营养素</h2>
          {todayCal > 0 ? (
            <div className="flex items-center justify-center gap-6">
              <div className="w-32 h-32">
                <Doughnut
                  data={doughnutData}
                  options={{
                    cutout: '65%',
                    plugins: { legend: { display: false } },
                  }}
                />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2"><span className="w-3 h-3 bg-yellow-400 rounded-full" />碳水 {formatGram(todayCarb)}</div>
                <div className="flex items-center gap-2"><span className="w-3 h-3 bg-primary-500 rounded-full" />蛋白质 {formatGram(todayProtein)}</div>
                <div className="flex items-center gap-2"><span className="w-3 h-3 bg-orange-500 rounded-full" />脂肪 {formatGram(todayFat)}</div>
              </div>
            </div>
          ) : (
            <div className="h-32 flex items-center justify-center text-gray-400 text-sm">暂无数据</div>
          )}
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">📅 今日摘要</h2>
          <div className="space-y-3">
            <div className="flex justify-between"><span className="text-sm text-gray-500">餐次记录</span><span className="font-semibold">{mealCount} 次</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">总热量</span><span className="font-semibold text-primary-600">{formatCalories(todayCal)}</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">蛋白质</span><span className="font-semibold text-primary-600">{formatGram(todayProtein)}</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">脂肪</span><span className="font-semibold text-primary-600">{formatGram(todayFat)}</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">碳水</span><span className="font-semibold text-yellow-600">{formatGram(todayCarb)}</span></div>
          </div>
        </div>
      </div>

      {records.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-800 mb-4">📝 最近饮食记录</h2>
          <div className="space-y-2">
            {records.slice(0, 10).map((r) => (
              <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <span className="text-sm font-medium text-gray-700">{r.food_name}</span>
                  <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{getMealTypeLabel(r.meal_type)}</span>
                </div>
                <div className="text-sm text-gray-500">
                  <span className="text-primary-600 font-medium">{formatCalories(r.calories)}</span>
                  <span className="mx-2 text-gray-300">|</span>
                  <span>{r.recorded_at?.slice(11, 16)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
