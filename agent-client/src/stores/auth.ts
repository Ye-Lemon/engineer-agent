import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { UpdateUserRequest, User } from '@/types'
import * as authApi from '@/api/auth'
import {
  clearUserInfo,
  getToken,
  getUserInfo,
  removeToken,
  saveToken,
  saveUserInfo,
} from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(getUserInfo())
  const accessToken = ref<string | null>(getToken())

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value))

  async function login(credentials: { username: string; password: string }) {
    const response = await authApi.login(credentials)

    accessToken.value = response.token
    user.value = response.userinfo
    saveToken(response.token)
    saveUserInfo(response.userinfo)

    return response
  }

  async function phoneLogin(phone: string, code: string) {
    const response = await authApi.phoneLogin({ phone, code, purpose: 'login' })
    accessToken.value = response.token
    user.value = response.userinfo
    saveToken(response.token)
    saveUserInfo(response.userinfo)
    return response
  }

  function setSession(response: { token: string; userinfo: User }) {
    accessToken.value = response.token
    user.value = response.userinfo
    saveToken(response.token)
    saveUserInfo(response.userinfo)
  }

  async function register(userInfo: {
    username: string
    email: string
    password: string
    confirm_password: string
  }) {
    return authApi.register(userInfo)
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      accessToken.value = null
      user.value = null
      removeToken()
      clearUserInfo()
    }
  }

  async function refreshUser() {
    const currentUser = await authApi.getCurrentUser()
    user.value = currentUser
    saveUserInfo(currentUser)
    return currentUser
  }

  async function updateUser(userInfo: UpdateUserRequest) {
    const updatedUser = await authApi.updateCurrentUser(userInfo)
    user.value = updatedUser
    saveUserInfo(updatedUser)
    return updatedUser
  }

  function initAuth() {
    accessToken.value = getToken()
    user.value = getUserInfo()
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    login,
    phoneLogin,
    setSession,
    register,
    refreshUser,
    updateUser,
    logout,
    initAuth,
  }
})
