<template>
  <div class="register-page">
    <section class="brand-panel">
      <img src="@/assets/logo.svg" alt="小P" class="logo" />
      <h1>小P</h1>
      <p>工程 AI 智能助手</p>
    </section>

    <main class="form-panel">
      <div class="auth-box">
        <h2>创建小P账号</h2>
        <p class="hint">注册后即可使用智能文档处理和工程知识问答</p>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="submitRegister"
        >
          <el-form-item prop="username">
            <el-input v-model="form.username" size="large" placeholder="用户名" autocomplete="username" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="form.email" size="large" placeholder="邮箱" autocomplete="email" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              size="large"
              type="password"
              show-password
              placeholder="密码（8-20个字符）"
              autocomplete="new-password"
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              size="large"
              type="password"
              show-password
              placeholder="确认密码"
              autocomplete="new-password"
              @keyup.enter="submitRegister"
            />
          </el-form-item>

          <el-button
            type="primary"
            native-type="submit"
            size="large"
            :loading="loading"
            class="submit"
          >
            {{ loading ? '注册中…' : '注册' }}
          </el-button>
        </el-form>

        <p class="switch-auth">
          已有账号？
          <router-link to="/login">返回登录</router-link>
        </p>
        <p class="footer">注册即代表同意服务条款和隐私政策</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuth } from '@/composables/useAuth'

const { handleRegister } = useAuth()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 6, max: 20, message: '用户名长度为 6-20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为 8-20 个字符', trigger: 'blur' },
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
}

async function submitRegister() {
  if (!formRef.value || loading.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await handleRegister(form.username.trim(), form.email.trim(), form.password, form.confirmPassword)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page { min-height: 100vh; display: flex; background: #f6f8fb; color: #1f2937; }
.brand-panel { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.brand-panel .logo { width: 92px; height: 92px; margin-bottom: 22px; animation: logoFloat 4s ease-in-out infinite; }
.brand-panel h1 { margin: 0; font-size: 38px; font-weight: 700; }
.brand-panel p { margin-top: 12px; color: rgba(255, 255, 255, 0.9); }
.form-panel { flex: 1; display: flex; justify-content: center; align-items: center; padding: 48px; background: white; }
.auth-box { width: min(410px, 100%); animation: authEnter .45s cubic-bezier(.22, 1, .36, 1) both; }
.auth-box h2 { margin: 0; font-size: 30px; line-height: 1.25; color: #667eea; letter-spacing: 0; }
.hint { color: #7b8794; font-size: 14px; line-height: 1.6; margin: 10px 0 28px; }
.submit { width: 100%; height: 44px; margin-top: 8px; border: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.submit:hover { filter: brightness(1.04); box-shadow: 0 8px 20px rgba(102, 126, 234, .22); }
.submit:active { transform: translateY(1px); }
.switch-auth { color: #7b8794; text-align: center; font-size: 14px; margin: 22px 0 0; }
.switch-auth a { color: #667eea; font-weight: 600; text-decoration: none; }
.switch-auth a:hover { color: #764ba2; text-decoration: underline; }
.footer { color: #9aa4b2; text-align: center; font-size: 12px; margin-top: 24px; }
@keyframes logoFloat { 0%, 100% { transform: translateY(0) rotate(-1deg); } 50% { transform: translateY(-8px) rotate(1deg); } }
@keyframes authEnter { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .brand-panel .logo, .auth-box { animation: none; } }
@media (max-width: 760px) { .brand-panel { display: none; } .form-panel { min-height: 100vh; padding: 28px 20px; } .auth-box { width: min(410px, 100%); } }
</style>
