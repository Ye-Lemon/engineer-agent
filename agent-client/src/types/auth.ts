export interface User {
  user_id: number
  username: string
  phone: string | null
  email: string | null
}

export interface LoginRequest {
  username: string
  password: string
}

export interface PhoneCodeRequest {
  phone: string
  code: string
  purpose?: 'login' | 'register'
}

export interface SendCodeRequest {
  phone: string
  purpose?: 'login' | 'register'
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirm_password?: string
}

export interface AuthResponse {
  token: string
  userinfo: User
}

export interface SendCodeResponse {
  expires_in: number
  cooldown: number
  debug_code?: string
}

export interface UpdateUserRequest {
  username: string
  phone: string | null
  email: string | null
}
