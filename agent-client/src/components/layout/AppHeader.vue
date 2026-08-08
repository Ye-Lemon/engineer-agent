<template>
  <header class="app-header">
    <div class="header-left">
      <el-button v-if="isMobile" text title="打开导航" @click="$emit('menu-toggle')"><el-icon :size="20"><Expand /></el-icon></el-button>
      <h2>{{ pageTitle }}</h2>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useResponsive } from '@/composables/useResponsive'
import { Expand } from '@element-plus/icons-vue'
const { isMobile } = useResponsive()
const route = useRoute()
const pageTitle = computed(() => (route.meta.title as string) || '工作台')
defineEmits<{ 'menu-toggle': [] }>()
</script>

<style scoped lang="scss">
.app-header { height: 52px; padding: 0 22px; flex: 0 0 auto; border-bottom: 1px solid var(--line); background: #fff; display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 10px; }
h2 { margin: 0; font-size: 14px; font-weight: 600; }
</style>
