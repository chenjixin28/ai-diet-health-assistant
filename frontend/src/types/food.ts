export interface FoodRecord {
  id: number
  user_id: number
  food_name: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  image_url: string | null
  calories: number
  protein: number
  fat: number
  carbohydrates: number
  serving_size: string | null
  recorded_at: string
}

export interface FoodRecognizeResult {
  food_name: string
  calories: number
  protein: number
  fat: number
  carbohydrates: number
  serving_size: string
  confidence: number
}

export interface NutritionLog {
  id: number
  user_id: number
  log_date: string
  total_calories: number
  total_protein: number
  total_fat: number
  total_carbohydrates: number
}
