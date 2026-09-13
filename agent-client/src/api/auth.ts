import request from './client'
import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse, PhoneCodeRequest, SendCodeRequest, SendCodeResponse, UpdateUserRequest, User } from '@/types'

function normalizeAuthResponse(value: AuthResponse | ApiResponse<AuthResponse> | Record<string, any>): AuthResponse {
  const payload = (value as ApiResponse<AuthResponse>).data ?? value
  const response = payload as Record<string, any>

  return {
    token: response.token ?? response.access_token,
    userinfo: response.userinfo ?? response.userInfo ?? response.user,
  } as AuthResponse
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const axiosResponse = await request.post<AuthResponse | ApiResponse<AuthResponse>>('/auth/login', data)
  return normalizeAuthResponse(axiosResponse as unknown as AuthResponse | ApiResponse<AuthResponse>)
}

export async function sendSmsCode(data: SendCodeRequest): Promise<SendCodeResponse> {
  const response = await request.post<SendCodeResponse | ApiResponse<SendCodeResponse>>('/auth/sms/send', data)
  const value = response as unknown as SendCodeResponse | ApiResponse<SendCodeResponse>
  return (value as ApiResponse<SendCodeResponse>).data ?? (value as SendCodeResponse)
}

export async function phoneLogin(data: PhoneCodeRequest): Promise<AuthResponse> {
  const response = await request.post<AuthResponse | ApiResponse<AuthResponse>>('/auth/phone/login', data)
  return normalizeAuthResponse(response as unknown as AuthResponse | ApiResponse<AuthResponse>)
}

export async function wechatAuthorize(redirect_uri: string): Promise<{ authorize_url: string; state: string }> {
  const response = await request.get<{ authorize_url: string; state: string } | ApiResponse<{ authorize_url: string; state: string }>>('/auth/wechat/authorize', { params: { redirect_uri } })
  const value = response as unknown as { authorize_url: string; state: string } | ApiResponse<{ authorize_url: string; state: string }>
  return (value as ApiResponse<{ authorize_url: string; state: string }>).data ?? (value as { authorize_url: string; state: string })
}

export async function wechatCallback(code: string, state: string): Promise<AuthResponse> {
  const response = await request.get<AuthResponse | ApiResponse<AuthResponse>>('/auth/wechat/callback', { params: { code, state } })
  return normalizeAuthResponse(response as unknown as AuthResponse | ApiResponse<AuthResponse>)
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
