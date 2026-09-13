<template>
  <div class="login-page">
    <section class="brand-panel">
      <div class="bubble-field" aria-hidden="true">
        <i v-for="bubble in 14" :key="bubble" class="bubble" :class="`bubble-${bubble}`"></i>
      </div>
      <img src="@/assets/logo.svg" alt="小P" class="logo" />
      <h1>小P</h1>
      <p>工程 AI 智能助手</p>
    </section>
    <main class="form-panel">
      <div class="auth-box">
        <h2>登录小P</h2>
        <p class="hint">手机号登录，首次使用将自动创建账号</p>
        <el-tabs v-model="mode" stretch>
          <el-tab-pane label="手机号登录" name="phone">
            <el-form ref="phoneFormRef" :model="phoneForm" :rules="phoneRules" @submit.prevent="submitPhone">
              <el-form-item prop="phone"><el-input v-model="phoneForm.phone" size="large" maxlength="11" placeholder="手机号" /></el-form-item>
              <el-form-item prop="code">
                <div class="code-row"><el-input v-model="phoneForm.code" size="large" maxlength="6" placeholder="验证码" /><el-button size="large" :disabled="countdown > 0" @click="requestCode">{{ countdown ? `${countdown}s 后重发` : '获取验证码' }}</el-button></div>
              </el-form-item>
              <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit">登录 / 注册</el-button>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="密码登录" name="password">
            <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" @submit.prevent="submitPassword">
              <el-form-item prop="username"><el-input v-model="passwordForm.username" size="large" placeholder="用户名" /></el-form-item>
              <el-form-item prop="password"><el-input v-model="passwordForm.password" size="large" type="password" show-password placeholder="密码" /></el-form-item>
              <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit">登录</el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        <el-button class="wechat" size="large" @click="loginWithWechat"><span class="wechat-mark">W</span> 微信登录</el-button>
        <el-button class="register-button" size="large" @click="$router.push('/register')">注册新账号</el-button>
        <p class="footer">登录即代表同意服务条款和隐私政策</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import * as authApi from '@/api/auth'
import { useAuth } from '@/composables/useAuth'

const { authStore, handleLogin, handlePhoneLogin } = useAuth()
const mode = ref('phone')
const loading = ref(false)
const countdown = ref(0)
const phoneFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const phoneForm = reactive({ phone: '', code: '' })
const passwordForm = reactive({ username: '', password: '' })
const phoneRule = { pattern: /^1[3-9]\\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
const phoneRules = { phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }, phoneRule], code: [{ required: true, message: '请输入验证码', trigger: 'blur' }] }
const passwordRules = { username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], password: [{ required: true, message: '请输入密码', trigger: 'blur' }] }

async function requestCode() {
  if (!phoneRule.pattern.test(phoneForm.phone)) return ElMessage.warning('请输入有效的手机号')
  try {
    const result = await authApi.sendSmsCode({ phone: phoneForm.phone, purpose: 'login' })
    if (result.debug_code) ElMessage.info(`开发验证码：${result.debug_code}`)
    countdown.value = result.cooldown || 60
    const timer = window.setInterval(() => { countdown.value -= 1; if (countdown.value <= 0) window.clearInterval(timer) }, 1000)
  } catch { /* interceptor shows the server error */ }
}

async function submitPhone() {
  if (!phoneFormRef.value || loading.value) return
  const valid = await phoneFormRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await handlePhoneLogin(phoneForm.phone, phoneForm.code) } finally { loading.value = false }
}

async function submitPassword() {
  if (!passwordFormRef.value || loading.value) return
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await handleLogin(passwordForm.username.trim(), passwordForm.password) } finally { loading.value = false }
}

async function loginWithWechat() {
  try {
    const { authorize_url } = await authApi.wechatAuthorize(`${window.location.origin}/auth/wechat/callback`)
    window.location.href = authorize_url
  } catch { /* unconfigured OAuth is reported by the interceptor */ }
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')
  const state = params.get('state')
  if (!code || !state) return
  try {
    authStore.setSession(await authApi.wechatCallback(code, state))
    window.history.replaceState({}, '', '/login')
    window.location.href = '/'
  } catch { /* interceptor shows the server error */ }
})
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; background: #f6f8fb; color: #1f2937; }
.brand-panel { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; overflow: hidden; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.bubble-field { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.bubble { position: absolute; display: block; border-radius: 50%; width: var(--size); height: var(--size); left: var(--left); top: var(--top); opacity: .3; background: radial-gradient(circle at 32% 28%, rgba(255,255,255,.82), rgba(255,255,255,.2) 42%, rgba(255,255,255,.05) 72%); box-shadow: inset -5px -6px 12px rgba(73,54,145,.12), 0 8px 22px rgba(38,23,102,.12); animation: bubbleDrift var(--duration) ease-in-out var(--delay) infinite alternate; }
.bubble-1 { --size: 88px; --left: 8%; --top: 16%; --duration: 12s; --delay: -4s; }
.bubble-2 { --size: 34px; --left: 25%; --top: 8%; --duration: 9s; --delay: -2s; }
.bubble-3 { --size: 56px; --left: 42%; --top: 20%; --duration: 14s; --delay: -8s; }
.bubble-4 { --size: 22px; --left: 73%; --top: 12%; --duration: 10s; --delay: -3s; }
.bubble-5 { --size: 112px; --left: 78%; --top: 28%; --duration: 16s; --delay: -10s; }
.bubble-6 { --size: 46px; --left: 13%; --top: 42%; --duration: 11s; --delay: -6s; }
.bubble-7 { --size: 70px; --left: 31%; --top: 48%; --duration: 13s; --delay: -1s; }
.bubble-8 { --size: 28px; --left: 58%; --top: 43%; --duration: 8s; --delay: -5s; }
.bubble-9 { --size: 96px; --left: 84%; --top: 54%; --duration: 15s; --delay: -7s; }
.bubble-10 { --size: 38px; --left: 4%; --top: 70%; --duration: 10s; --delay: -2s; }
.bubble-11 { --size: 62px; --left: 22%; --top: 78%; --duration: 12s; --delay: -9s; }
.bubble-12 { --size: 26px; --left: 49%; --top: 72%; --duration: 9s; --delay: -4s; }
.bubble-13 { --size: 76px; --left: 66%; --top: 82%; --duration: 14s; --delay: -11s; }
.bubble-14 { --size: 44px; --left: 91%; --top: 76%; --duration: 11s; --delay: -6s; }
.brand-panel > * { position: relative; z-index: 1; }
.brand-panel .logo { width: 92px; height: 92px; margin-bottom: 22px; animation: logoFloat 4s ease-in-out infinite; }
.brand-panel h1 { margin: 0; font-size: 38px; font-weight: 700; }
.brand-panel p { margin-top: 12px; color: rgba(255, 255, 255, 0.9); }
.form-panel { flex: 1; display: flex; justify-content: center; align-items: center; padding: 48px; background: white; }
.auth-box { width: min(410px, 100%); animation: authEnter .45s cubic-bezier(.22, 1, .36, 1) both; }
.auth-box h2 { margin: 0; font-size: 30px; line-height: 1.25; color: #667eea; letter-spacing: 0; }
.hint { color: #7b8794; font-size: 14px; line-height: 1.6; margin: 10px 0 28px; }
.code-row { display: flex; gap: 10px; width: 100%; }
.code-row .el-input { flex: 1; }
.code-row .el-button { width: 116px; }
.submit, .wechat { width: 100%; height: 44px; margin-top: 8px; }
.submit { border: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.submit:hover { filter: brightness(1.04); box-shadow: 0 8px 20px rgba(102, 126, 234, .22); }
.submit:active, .wechat:active { transform: translateY(1px); }
.wechat { color: #1aad70; border-color: #b8e6d2; }
.wechat-mark { font-weight: 700; margin-right: 7px; }
.register-button { display: block; width: 100%; height: 44px; margin: 10px 0 0; color: #667eea; border-color: #d9d7f8; background: #fff; }
.register-button:hover { color: #764ba2; border-color: #b9b2ef; background: #faf9ff; }
.footer { color: #9aa4b2; text-align: center; font-size: 12px; margin-top: 24px; }
@keyframes logoFloat { 0%, 100% { transform: translateY(0) rotate(-1deg); } 50% { transform: translateY(-8px) rotate(1deg); } }
@keyframes bubbleDrift { 0% { transform: translate3d(-10px, 8px, 0) scale(.96); } 50% { transform: translate3d(12px, -16px, 0) scale(1.04); } 100% { transform: translate3d(-4px, -28px, 0) scale(.98); } }
@keyframes authEnter { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .bubble, .brand-panel .logo, .auth-box { animation: none; } }
@media (max-width: 760px) { .brand-panel { display: none; } .form-panel { min-height: 100vh; padding: 28px 20px; } .auth-box { width: min(410px, 100%); } }
</style>
