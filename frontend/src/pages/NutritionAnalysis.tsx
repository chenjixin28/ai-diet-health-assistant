import { useState, useEffect, useRef } from 'react'
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

  const [showAddDialog, setShowAddDialog] = useState(false)
  const [addFood, setAddFood] = useState('')
  const [addMeal, setAddMeal] = useState('lunch')
  const [addCal, setAddCal] = useState('')
  const [addProtein, setAddProtein] = useState('')
  const [addFat, setAddFat] = useState('')
  const [addCarb, setAddCarb] = useState('')
  const [addServing, setAddServing] = useState('')
  const [addLoading, setAddLoading] = useState(false)

  const [advice, setAdvice] = useState('')
  const [adviceLoading, setAdviceLoading] = useState(false)
  const adviceRef = useRef<HTMLDivElement>(null)

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
    } catch {
      showToast('获取营养数据失败', 'error')
    }
  }

  useEffect(() => {
    fetchData()
  }, [days])

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`确定删除「${name}」这条记录吗？`)) return
    try {
      const { data } = await foodApi.deleteRecord(id)
      if (data.success) {
        showToast('记录已删除', 'success')
        fetchData()
      } else {
        showToast(data.detail || '删除失败', 'error')
      }
    } catch {
      showToast('删除失败', 'error')
    }
  }

  const handleAddFood = async () => {
    if (!addFood.trim() || !addCal) {
      showToast('请填写食物名称和热量', 'error')
      return
    }
    setAddLoading(true)
    try {
      const { data } = await foodApi.addRecord({
        food_name: addFood,
        meal_type: addMeal,
        calories: parseInt(addCal) || 0,
        protein: parseInt(addProtein) || 0,
        fat: parseInt(addFat) || 0,
        carbohydrates: parseInt(addCarb) || 0,
        serving_size: addServing || undefined,
      })
      if (data.success) {
        showToast('记录已添加', 'success')
        setShowAddDialog(false)
        setAddFood('')
        setAddCal('')
        setAddProtein('')
        setAddFat('')
        setAddCarb('')
        setAddServing('')
        fetchData()
      } else {
        showToast(data.detail || '添加失败', 'error')
      }
    } catch {
      showToast('添加失败', 'error')
    } finally {
      setAddLoading(false)
    }
  }

  const handleGetAdvice = async () => {
    setAdviceLoading(true)
    setAdvice('')
    try {
      const { data: resp } = await nutritionApi.getAdvice()
      if (resp.success && resp.data?.advice) {
        setAdvice(resp.data.advice)
      } else {
        showToast('获取建议失败', 'error')
      }
      adviceRef.current?.scrollIntoView({ behavior: 'smooth' })
    } catch {
      showToast('获取建议失败', 'error')
    } finally {
      setAdviceLoading(false)
    }
  }

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

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack']

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
                <div className="flex items-center gap-2"><span className="w-3 h-3 bg-blue-500 rounded-full" />蛋白质 {formatGram(todayProtein)}</div>
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
            <div className="flex justify-between"><span className="text-sm text-gray-500">蛋白质</span><span className="font-semibold text-blue-600">{formatGram(todayProtein)}</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">脂肪</span><span className="font-semibold text-accent-600">{formatGram(todayFat)}</span></div>
            <div className="flex justify-between"><span className="text-sm text-gray-500">碳水</span><span className="font-semibold text-yellow-600">{formatGram(todayCarb)}</span></div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">📝 饮食记录</h2>
          <button
            onClick={() => setShowAddDialog(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            + 手动添加
          </button>
        </div>

        {records.length > 0 ? (
          <div className="space-y-2">
            {records.map((r) => (
              <div key={r.id} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                <div className="flex-1">
                  <span className="text-sm font-medium text-gray-700">{r.food_name}</span>
                  <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{getMealTypeLabel(r.meal_type)}</span>
                  {r.serving_size && <span className="ml-2 text-xs text-gray-400">{r.serving_size}</span>}
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-sm text-right">
                    <span className="text-primary-600 font-medium">{formatCalories(r.calories)}</span>
                    <span className="mx-1 text-gray-300">|</span>
                    <span className="text-gray-400">{r.recorded_at?.slice(11, 16)}</span>
                  </div>
                  <button
                    onClick={() => handleDelete(r.id, r.food_name)}
                    className="text-red-400 hover:text-red-600 text-sm px-2 py-1 rounded hover:bg-red-50 transition-colors"
                    title="删除"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400 text-center py-6">暂无记录，去"食物识别"拍照或点击手动添加</p>
        )}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">🤖 AI 膳食建议</h2>
          <button
            onClick={handleGetAdvice}
            disabled={adviceLoading}
            className="px-5 py-2 bg-gradient-to-r from-primary-600 to-green-600 text-white rounded-lg text-sm font-medium hover:from-primary-700 hover:to-green-700 transition-colors disabled:opacity-50"
          >
            {adviceLoading ? '分析中...' : '获取AI建议'}
          </button>
        </div>
        {advice ? (
          <div ref={adviceRef} className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap bg-green-50 rounded-lg p-4">
            {advice}
          </div>
        ) : (
          <p className="text-sm text-gray-400 text-center py-4">
            点击上方按钮，AI 将根据今日饮食数据给出个性化建议
          </p>
        )}
      </div>

      {showAddDialog && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={() => setShowAddDialog(false)}>
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">手动添加食物</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-500 mb-1">食物名称 *</label>
                <input value={addFood} onChange={(e) => setAddFood(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="如：红烧肉" />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">餐次</label>
                <div className="flex gap-2">
                  {mealTypes.map((mt) => (
                    <button key={mt} onClick={() => setAddMeal(mt)}
                      className={`flex-1 py-1.5 rounded text-xs font-medium border ${
                        addMeal === mt ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 text-gray-500'
                      }`}
                    >{getMealTypeLabel(mt)}</button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm text-gray-500 mb-1">热量 (kcal) *</label>
                  <input type="number" value={addCal} onChange={(e) => setAddCal(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="200" />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">份量</label>
                  <input value={addServing} onChange={(e) => setAddServing(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="约200g" />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">蛋白质 (g)</label>
                  <input type="number" value={addProtein} onChange={(e) => setAddProtein(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="10" />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">脂肪 (g)</label>
                  <input type="number" value={addFat} onChange={(e) => setAddFat(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="5" />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">碳水 (g)</label>
                  <input type="number" value={addCarb} onChange={(e) => setAddCarb(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-400" placeholder="30" />
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={handleAddFood} disabled={addLoading}
                className="flex-1 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
              >{addLoading ? '添加中...' : '添加'}</button>
              <button onClick={() => setShowAddDialog(false)}
                className="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
