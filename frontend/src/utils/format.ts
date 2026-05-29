import type { NutritionSummary } from '../types/nutrition'

export function formatCalories(kcal: number): string {
  return `${Math.round(kcal)} kcal`
}

export function formatGram(g: number): string {
  return `${g.toFixed(1)}g`
}

export function getHealthGoalLabel(goal: string): string {
  const map: Record<string, string> = {
    lose_fat: '减脂',
    build_muscle: '增肌',
    control_sugar: '控糖',
  }
  return map[goal] || goal
}

export function getMealTypeLabel(type: string): string {
  const map: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '零食',
  }
  return map[type] || type
}

export function getTodayDateStr(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

export function calcCaloriePercentage(current: number, target: number): number {
  if (!target) return 0
  return Math.min(Math.round((current / target) * 100), 100)
}
