export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
}

export type HealthGoal = 'lose_fat' | 'build_muscle' | 'control_sugar'

export interface HealthProfile {
  height: number | null
  weight: number | null
  health_goal: HealthGoal | null
  target_weight: number | null
  daily_calorie_target: number | null
  daily_protein_target: number | null
  daily_fat_target: number | null
  daily_carb_target: number | null
}

export interface UserProfile extends User, HealthProfile {}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: number
  username: string
}

export interface ApiResponse<T = unknown> {
  success: boolean
  detail: string
  data: T
}
