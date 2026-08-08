import request from './client'
import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse, UpdateUserRequest, User } from '@/types'

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const axiosResponse = await request.post<AuthResponse | ApiResponse<AuthResponse>>('/auth/login', data)
  const response = axiosResponse as unknown as AuthResponse | ApiResponse<AuthResponse>
  const wrappedResponse = response as ApiResponse<AuthResponse>
  return wrappedResponse.data ?? (response as AuthResponse)
}

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<User> {
  const axiosResponse = await request.post<User | ApiResponse<User>>('/auth/register', data)
  const response = axiosResponse as unknown as User | ApiResponse<User>
  return (response as ApiResponse<User>).data ?? (response as User)
}

/**
 * 刷新Token
 */
/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<User> {
  const axiosResponse = await request.get<User | ApiResponse<User>>('/auth/info')
  const response = axiosResponse as unknown as User | ApiResponse<User>
  return (response as ApiResponse<User>).data ?? (response as User)
}

export async function updateCurrentUser(data: UpdateUserRequest): Promise<User> {
  const axiosResponse = await request.patch<User | ApiResponse<User>>('/auth/info', data)
  const response = axiosResponse as unknown as User | ApiResponse<User>
  return (response as ApiResponse<User>).data ?? (response as User)
}

/**
 * 用户登出
 */
export function logout(): Promise<void> {
  // 登出逻辑在前端处理，清除本地存储
  return request.post('/auth/logout')
}
