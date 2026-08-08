import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

/**
 * 认证相关逻辑的组合式函数
 */
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  /**
   * 用户登录
   */
  async function handleLogin(username: string, password: string) {
    try {
      await authStore.login({ username, password })
      ElMessage.success('登录成功')
      router.push('/')
    } catch (error: any) {
      ElMessage.error(error.message || '登录失败，请检查用户名和密码')
    }
  }

  /**
   * 用户注册
   */
  async function handleRegister(username: string, email: string, password: string, confirmPassword: string) {
    // 验证密码
    if (password !== confirmPassword) {
      ElMessage.error('两次输入的密码不一致')
      return
    }

    try {
      await authStore.register({ username, email, password, confirm_password: confirmPassword })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error: any) {
      ElMessage.error(error.message || '注册失败，请稍后重试')
    }
  }

  /**
   * 用户登出
   */
  async function handleLogout() {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }

  return {
    authStore,
    handleLogin,
    handleRegister,
    handleLogout,
  }
}
