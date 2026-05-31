import api from './axios'
import type { FoodRecognizeResult } from '../types/food'

export const foodApi = {
  recognizeImage: (file: File) => {
    const formData = new FormData()
    formData.append('image', file)
    return api.post<{ success: boolean; detail: string; items: FoodRecognizeResult[] }>(
      '/foods/recognize',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
  },

  addRecord: (record: {
    food_name: string
    meal_type: string
    calories: number
    protein: number
    fat: number
    carbohydrates: number
    serving_size?: string
    image_url?: string
  }) => api.post('/foods/record', record),

  getRecords: (params?: { date?: string; meal_type?: string }) =>
    api.get('/foods/records', { params }),

  searchFood: (keyword: string) =>
    api.post('/foods/search', { keyword }),

  deleteRecord: (id: number) =>
    api.delete(`/foods/records/${id}`),
}
