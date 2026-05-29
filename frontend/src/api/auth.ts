import api from './axios'
import type { ApiResponse, RegisterPayload, LoginPayload, LoginResponse, UserProfile, HealthProfile } from '../types/user'

export const authApi = {
  register: (payload: RegisterPayload) =>
    api.post<ApiResponse<{ user_id: number; username: string }>>('/auth/register', payload),

  login: (payload: LoginPayload) =>
    api.post<ApiResponse<LoginResponse>>('/auth/login', payload),

  getMe: () =>
    api.get<ApiResponse<UserProfile>>('/auth/me'),

  updateProfile: (payload: Partial<HealthProfile>) =>
    api.put<ApiResponse<null>>('/auth/profile', payload),
}
