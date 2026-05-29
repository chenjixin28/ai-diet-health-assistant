export interface NutritionSummary {
  date: string
  total_calories: number
  total_protein: number
  total_fat: number
  total_carbohydrates: number
  meal_count: number
}

export interface WeeklyReport {
  dates: string[]
  calories: number[]
  protein: number[]
  fat: number[]
  carbohydrates: number[]
}
