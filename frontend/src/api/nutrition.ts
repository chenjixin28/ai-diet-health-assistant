import api from './axios'

export const nutritionApi = {
  getSummary: (days: number = 7) =>
    api.get('/nutrition/summary', { params: { days } }),

  getToday: () =>
    api.get('/nutrition/today'),

  recommendMeal: (params: { health_goal?: string; target_calories?: number; preferences?: string }) =>
    api.get('/nutrition/recommend', {
      params,
      responseType: 'stream',
      headers: { Accept: 'text/event-stream' },
    }),

  getAdvice: () =>
    api.get('/nutrition/advice'),
}
