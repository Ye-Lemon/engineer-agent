<template>
  <div class="app-layout">
    <el-drawer v-if="shouldHideSidebar" v-model="drawerVisible" direction="ltr" :size="232" :with-header="false">
      <AppSidebar :collapsed="false" @close="drawerVisible = false" />
    </el-drawer>
    <aside v-else class="sidebar-container" :class="{ collapsed: shouldCollapseSidebar }">
      <AppSidebar :collapsed="shouldCollapseSidebar" />
    </aside>
    <div class="main-container">
      <AppHeader @menu-toggle="drawerVisible = true" />
      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in"><component :is="Component" /></transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useResponsive } from '@/composables/useResponsive'
const { shouldCollapseSidebar, shouldHideSidebar } = useResponsive()
const drawerVisible = ref(false)
</script>

<style scoped lang="scss">
.app-layout { display: flex; height: 100vh; overflow: hidden; background: #fff; }
.sidebar-container { width: 232px; flex: 0 0 auto; border-right: 1px solid var(--line); transition: width .25s ease; }
.sidebar-container.collapsed { width: 64px; }
.main-container { flex: 1; min-width: 0; display: flex; flex-direction: column; overflow: hidden; }
.content-area { flex: 1; padding: 0; overflow-y: auto; background: #f8f7fb; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease, transform .2s ease; }
.fade-enter-from { opacity: 0; transform: translateY(6px); }
.fade-leave-to { opacity: 0; transform: translateY(-4px); }
@media (prefers-reduced-motion: reduce) {
  .fade-enter-active, .fade-leave-active { transition: none; }
}
:deep(.el-drawer__body) { padding: 0; }
</style>
