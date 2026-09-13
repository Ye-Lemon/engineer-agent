<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 初始化认证状态
  authStore.initAuth()
})
</script>

<style>
:root {
  --brand-50: #f7f5ff;
  --brand-100: #eee9ff;
  --brand-200: #ddd2ff;
  --brand-500: #7557d9;
  --brand-600: #6546ca;
  --brand-700: #5135aa;
  --ink-900: #1f1d2b;
  --ink-600: #686477;
  --line: #e9e6ef;
  --surface: #ffffff;
  --font-sans: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --shadow-soft: 0 12px 34px rgba(71, 51, 117, .08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.5;
  letter-spacing: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--ink-900);
  background: #fff;
}

#app {
  height: 100vh;
}

button, input, textarea { font: inherit; }
h1, h2, h3, p { overflow-wrap: anywhere; }
::selection { color: #fff; background: var(--brand-500); }

/* Shared product shell: calm surfaces, consistent radius and readable controls. */
.content-area > * { min-height: 100%; }
.content-area .el-card { border-radius: 16px; border-color: #e9e5ef; box-shadow: 0 12px 34px rgba(52, 40, 83, .06); }
.content-area .el-card__header { border-bottom-color: #f0edf5; }
.content-area .el-button { border-radius: 9px; }
.content-area .el-input__wrapper, .content-area .el-select .el-input__wrapper { border-radius: 9px; }
.content-area .el-table { border-radius: 10px; overflow: hidden; }
.content-area .el-empty { padding: 46px 0; }
</style>
