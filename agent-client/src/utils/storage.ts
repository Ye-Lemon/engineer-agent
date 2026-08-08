import type { User } from '@/types'

const TOKEN_KEY = 'access_token'
const USER_INFO_KEY = 'user_info'

/**
 * 保存Token
 */
export function saveToken(accessToken: string): void {
  localStorage.setItem(TOKEN_KEY, accessToken)
}

/**
 * 获取Access Token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 移除Token
 */
export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * 保存用户信息
 */
export function saveUserInfo(user: User): void {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(user))
}

/**
 * 获取用户信息
 */
export function getUserInfo(): User | null {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  if (!userInfo) return null
  
  try {
    return JSON.parse(userInfo)
  } catch {
    return null
  }
}

/**
 * 清除用户信息
 */
export function clearUserInfo(): void {
  localStorage.removeItem(USER_INFO_KEY)
}

/**
 * 清除所有认证数据
 */
export function clearAuth(): void {
  removeToken()
  clearUserInfo()
}
