import { useState, useRef, ChangeEvent } from 'react'
import { foodApi } from '../api/foods'
import { showToast } from '../components/common/Toast'
import type { FoodRecognizeResult } from '../types/food'
import { formatCalories, formatGram, getMealTypeLabel } from '../utils/format'

export function FoodRecognition() {
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [results, setResults] = useState<FoodRecognizeResult[]>([])
  const [loading, setLoading] = useState(false)
  const [addingIdx, setAddingIdx] = useState<number | null>(null)
  const [mealType, setMealType] = useState('lunch')
  const [addAllLoading, setAddAllLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack']

  const handleFile = async (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      showToast('图片不能超过 10MB', 'error')
      return
    }
    const reader = new FileReader()
    reader.onload = () => setImagePreview(reader.result as string)
    reader.readAsDataURL(file)

    setLoading(true)
    setResults([])
    try {
      const { data } = await foodApi.recognizeImage(file)
      if (data.success) {
        setResults(data.items)
        showToast(`识别到 ${data.items.length} 种食物`, 'success')
      } else {
        showToast(data.detail || '识别失败', 'error')
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : '网络错误', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleAddRecord = async (item: FoodRecognizeResult, index: number) => {
    setAddingIdx(index)
    try {
      await foodApi.addRecord({
        food_name: item.food_name,
        meal_type: mealType,
        calories: item.calories,
        protein: item.protein,
        fat: item.fat,
        carbohydrates: item.carbohydrates,
        serving_size: item.serving_size,
      })
      showToast(`${item.food_name} 已添加到${getMealTypeLabel(mealType)}记录`, 'success')
      setResults((prev) => prev.filter((_, i) => i !== index))
    } catch (err) {
      showToast(err instanceof Error ? err.message : '添加失败', 'error')
    } finally {
      setAddingIdx(null)
    }
  }

  const handleAddAll = async () => {
    if (results.length === 0) return
    setAddAllLoading(true)
    let successCount = 0
    for (const item of results) {
      try {
        await foodApi.addRecord({
          food_name: item.food_name,
          meal_type: mealType,
          calories: item.calories,
          protein: item.protein,
          fat: item.fat,
          carbohydrates: item.carbohydrates,
          serving_size: item.serving_size,
        })
        successCount++
      } catch {
      }
    }
    if (successCount > 0) {
      showToast(`已添加 ${successCount} 种食物到${getMealTypeLabel(mealType)}记录`, 'success')
      setResults([])
    } else {
      showToast('添加失败，请重试', 'error')
    }
    setAddAllLoading(false)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">📸 食物识别</h1>

      <div className="flex gap-3 flex-wrap items-center">
        {mealTypes.map((mt) => (
          <button
            key={mt}
            onClick={() => setMealType(mt)}
            className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
              mealType === mt
                ? 'bg-primary-50 text-primary-700 border-primary-300'
                : 'text-gray-500 border-gray-200 hover:border-gray-300'
            }`}
          >
            {getMealTypeLabel(mt)}
          </button>
        ))}
        {results.length > 1 && (
          <button
            onClick={handleAddAll}
            disabled={addAllLoading}
            className="ml-auto px-5 py-2 rounded-full text-sm font-medium bg-green-600 text-white hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            {addAllLoading ? '添加中...' : `一键添加全部到${getMealTypeLabel(mealType)}`}
          </button>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        className="hidden"
      />

      {!imagePreview ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          className="bg-white rounded-xl p-10 shadow-sm border-2 border-dashed border-gray-200 text-center hover:border-primary-400 hover:bg-primary-50/30 transition-colors cursor-pointer"
        >
          <span className="text-6xl block mb-4">📸</span>
          <p className="text-lg font-medium text-gray-700">点击选择食物图片</p>
          <p className="text-sm text-gray-400 mt-1">支持 JPG / PNG / WEBP，最大 10MB</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <img src={imagePreview} alt="食物" className="w-full h-64 object-cover" />
            <div className="p-3 flex gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors"
              >
                换一张
              </button>
              <button
                onClick={() => {
                  setImagePreview(null)
                  setResults([])
                }}
                className="flex-1 py-2 border border-red-200 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
              >
                清除
              </button>
            </div>
          </div>

          <div>
            {loading ? (
              <div className="bg-white rounded-xl p-10 shadow-sm border border-gray-100 text-center">
                <div className="animate-spin w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-4" />
                <p className="text-gray-500">YOLO模型识别中...</p>
              </div>
            ) : results.length > 0 ? (
              <div className="space-y-3">
                {results.map((item, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-semibold text-gray-900">🍽️ {item.food_name}</p>
                        <p className="text-xs text-gray-400">置信度 {Math.round(item.confidence * 100)}% · {item.serving_size}</p>
                      </div>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-primary-100 text-primary-700">
                        {formatCalories(item.calories)}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center text-sm">
                      <div className="bg-gray-50 rounded-lg p-2">
                        <p className="text-xs text-gray-400">蛋白质</p>
                        <p className="font-bold text-blue-600">{formatGram(item.protein)}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-2">
                        <p className="text-xs text-gray-400">脂肪</p>
                        <p className="font-bold text-accent-600">{formatGram(item.fat)}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-2">
                        <p className="text-xs text-gray-400">碳水</p>
                        <p className="font-bold text-yellow-600">{formatGram(item.carbohydrates)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAddRecord(item, idx)}
                      disabled={addingIdx === idx}
                      className="mt-3 w-full py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
                    >
                      {addingIdx === idx ? '添加中...' : `添加到${getMealTypeLabel(mealType)}记录`}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl p-10 shadow-sm border border-gray-100 text-center">
                <span className="text-4xl block mb-3">🔍</span>
                <p className="text-gray-500">等待识别结果</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
