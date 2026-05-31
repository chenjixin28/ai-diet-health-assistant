import api from './axios'

export const checkinApi = {
  getCalendar: (year?: number, month?: number) =>
    api.get('/checkin/calendar', { params: { year, month } }),

  getAchievements: () =>
    api.get('/checkin/achievements'),
}
