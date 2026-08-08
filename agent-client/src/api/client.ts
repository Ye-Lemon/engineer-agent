import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()

    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }

    return config
  },
  (error) => Promise.reject(error),
)

service.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  async (error) => {
    const isAuthRequest = /\/auth\/(login|register)$/.test(error.config?.url || '')
    if (error.response?.status === 401 && !isAuthRequest) {
      const authStore = useAuthStore()
      await authStore.logout()

      if (window.location.pathname !== '/login') {
        ElMessage.error('登录已过期，请重新登录')
        window.location.href = '/login'
      }
    }

    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      '请求失败'
    ElMessage.error(message)

    return Promise.reject(error)
  },
)

export function setupAxiosDefaults(config: AxiosRequestConfig) {
  Object.assign(service.defaults, config)
}

export default service
