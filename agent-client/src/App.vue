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
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--ink-900);
  background: #fff;
}

#app {
  height: 100vh;
}

button, input, textarea { font: inherit; }
::selection { color: #fff; background: var(--brand-500); }
</style>
