<template>
  <div class="register-view">
    <!-- 左侧品牌区域 -->
    <div class="left-panel">
      <!-- 浮动气泡 -->
      <div class="bubbles">
        <div class="bubble" v-for="i in 15" :key="i" :style="getBubbleStyle(i)"></div>
      </div>
      
      <div class="brand-content">
        <img src="@/assets/logo.svg" alt="Logo" class="brand-logo" />
        <h1 class="brand-title">
          <span class="title-main">工程AI智能体</span>
          <span class="title-name">小向</span>
        </h1>
        <p class="brand-description">您的智能化工程管理助手</p>
        <div class="brand-features">
          <div class="feature-item">
            <el-icon><Document /></el-icon>
            <span>智能文档处理</span>
          </div>
          <div class="feature-item">
            <el-icon><Search /></el-icon>
            <span>RAG 知识检索</span>
          </div>
          <div class="feature-item">
            <el-icon><DocumentCopy /></el-icon>
            <span>自动生成报告</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧注册表单区域 -->
    <div class="right-panel">
      <div class="register-container">
        <div class="register-header">
          <h2>创建账号</h2>
          <p class="subtitle">加入我们，开启智能工程管理之旅</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegisterSubmit" class="register-form">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="邮箱"
              prefix-icon="Message"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleRegisterSubmit"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              native-type="submit"
              :loading="loading"
              class="register-btn"
            >
              {{ loading ? '注册中...' : '注册' }}
            </el-button>
          </el-form-item>

          <div class="footer-links">
            <span>已有账号？</span>
            <router-link to="/login">立即登录</router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElForm } from 'element-plus'
import { Document, Search, DocumentCopy } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'

const { handleRegister } = useAuth()

const formRef = ref<InstanceType<typeof ElForm>>()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// 生成气泡样式
const getBubbleStyle = (_index: number) => {
  const size = Math.random() * 60 + 20 // 20-80px
  const left = Math.random() * 100 // 0-100%
  const top = Math.random() * 100 // 0-100%
  const delay = Math.random() * 10 // 0-10s
  const duration = Math.random() * 15 + 20 // 20-35s
  const opacity = Math.random() * 0.3 + 0.1 // 0.1-0.4
  const driftX = (Math.random() - 0.5) * 2 // -1 to 1
  const driftY = (Math.random() - 0.5) * 2 // -1 to 1
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    opacity: opacity,
    '--drift-x': driftX,
    '--drift-y': driftY,
  }
}

const validatePass = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 6, max: 20, message: '用户名长度在6-20个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度在8-20个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validatePass, trigger: 'blur' },
  ],
}

const handleRegisterSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await handleRegister(form.username, form.email, form.password, form.confirmPassword)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.register-view {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

// 左侧面板
.left-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="70" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
    opacity: 0.3;
  }
}

// 气泡容器
.bubbles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

// 单个气泡
.bubble {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.1));
  box-shadow: 
    inset 0 0 20px rgba(255, 255, 255, 0.3),
    0 0 20px rgba(255, 255, 255, 0.2);
  animation: bubbleFloat linear infinite;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

@keyframes bubbleFloat {
  0% {
    transform: translate(0, 0) rotate(0deg) scale(1);
  }
  25% {
    transform: translate(calc(var(--drift-x, 0) * 80px), calc(var(--drift-y, 0) * 80px)) rotate(90deg) scale(1.05);
  }
  50% {
    transform: translate(calc(var(--drift-x, 0) * 150px), calc(var(--drift-y, 0) * 150px)) rotate(180deg) scale(1);
  }
  75% {
    transform: translate(calc(var(--drift-x, 0) * 80px), calc(var(--drift-y, 0) * 80px)) rotate(270deg) scale(0.95);
  }
  100% {
    transform: translate(0, 0) rotate(360deg) scale(1);
  }
}

.brand-content {
  text-align: center;
  color: white;
  z-index: 1;
  max-width: 500px;
}

.brand-logo {
  width: 120px;
  height: 120px;
  margin-bottom: 30px;
  filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.2));
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.brand-title {
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;

  .title-main {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: 3px;
    text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .title-name {
    font-size: 56px;
    font-weight: 800;
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #d299c2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    filter: drop-shadow(0 4px 8px rgba(168, 237, 234, 0.4));
    animation: glow 3s ease-in-out infinite;
    letter-spacing: 8px;
  }
}

@keyframes glow {
  0%, 100% {
    filter: drop-shadow(0 4px 8px rgba(168, 237, 234, 0.4));
  }
  50% {
    filter: drop-shadow(0 6px 16px rgba(210, 153, 194, 0.6));
  }
}

.brand-description {
  font-size: 16px;
  margin: 0 0 50px;
  opacity: 0.95;
  letter-spacing: 2px;
  font-weight: 300;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateX(10px);
  }

  .el-icon {
    font-size: 20px;
  }
}

// 右侧面板
.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, transparent 100%);
  }
}

.register-container {
  width: 100%;
  max-width: 420px;
  z-index: 1;
}

.register-header {
  margin-bottom: 40px;

  h2 {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    font-size: 15px;
    color: #909399;
    margin: 0;
  }
}

.register-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-input__wrapper) {
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }

    &.is-focus {
      box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
    }
  }
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-top: 10px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}

.footer-links {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #606266;

  a {
    color: #667eea;
    text-decoration: none;
    margin-left: 8px;
    font-weight: 500;
    transition: all 0.3s ease;

    &:hover {
      color: #764ba2;
      text-decoration: underline;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .register-view {
    flex-direction: column;
  }

  .left-panel {
    display: none;
  }

  .right-panel {
    flex: 1;
    padding: 30px 20px;
  }
}
</style>
