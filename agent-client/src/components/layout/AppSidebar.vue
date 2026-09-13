<template>
  <div class="app-sidebar">
    <div class="sidebar-header" :class="{ compact: collapsed }">
      <img src="@/assets/logo.svg" alt="Logo" class="logo" />
      <span v-if="!collapsed" class="app-title">小P</span>
    </div>
    <div v-if="!collapsed" class="group-label">工作空间</div>
    <el-menu :default-active="activeMenu" :collapse="collapsed" router class="sidebar-menu">
      <el-menu-item v-for="item in items" :key="item.path" :index="item.path">
        <el-icon><component :is="item.icon" /></el-icon>
        <template #title>{{ item.label }}</template>
      </el-menu-item>
    </el-menu>
    <el-popover v-model:visible="accountMenuVisible" placement="top-start" :width="196" trigger="click" popper-class="account-popper">
      <template #reference>
        <button class="account-trigger" :class="{ compact: collapsed, active: accountMenuVisible }" type="button" aria-label="打开账号菜单">
          <el-avatar :size="34">{{ initial }}</el-avatar>
          <span v-if="!collapsed" class="account-name">{{ username }}</span>
          <el-icon v-if="!collapsed" class="more"><MoreFilled /></el-icon>
        </button>
      </template>
      <div class="account-menu">
        <div class="menu-group">
          <button type="button" @click="openSettings"><el-icon><Setting /></el-icon><span>系统设置</span></button>
          <button type="button" @click="openFiles"><el-icon><CollectionTag /></el-icon><span>知识资料</span><el-icon class="menu-arrow"><ArrowRight /></el-icon></button>
        </div>
        <div class="menu-group">
          <button type="button" @click="openApiService"><el-icon><Connection /></el-icon><span>API 服务</span></button>
        </div>
        <div class="menu-group">
          <button type="button" @click="switchAccount"><el-icon><Switch /></el-icon><span>切换账号</span><el-icon class="menu-arrow"><ArrowRight /></el-icon></button>
          <button type="button" @click="logoutFromMenu"><el-icon><SwitchButton /></el-icon><span>退出登录</span></button>
        </div>
      </div>
    </el-popover>

    <AccountSettingsDialog v-model="settingsVisible" />
    <ApiServiceDialog v-model="apiServiceVisible" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, CollectionTag, Connection, Document, Folder, HomeFilled, MoreFilled, Setting, Switch, SwitchButton } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import AccountSettingsDialog from '@/components/account/AccountSettingsDialog.vue'
import ApiServiceDialog from '@/components/account/ApiServiceDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'
defineProps<{ collapsed: boolean }>()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { handleLogout } = useAuth()
const accountMenuVisible = ref(false)
const settingsVisible = ref(false)
const apiServiceVisible = ref(false)
const username = computed(() => authStore.user?.username || 'User')
const initial = computed(() => username.value.charAt(0).toUpperCase())
const activeMenu = computed(() => route.path)
const items = [
  { path: '/', label: '工作台', icon: HomeFilled },
  { path: '/files', label: '知识空间', icon: Folder },
  { path: '/report', label: '报告生成', icon: Document },
]
function openSettings() { accountMenuVisible.value = false; settingsVisible.value = true }
function openFiles() { accountMenuVisible.value = false; router.push('/files') }
function openApiService() { accountMenuVisible.value = false; apiServiceVisible.value = true }
async function switchAccount() {
  accountMenuVisible.value = false
  try {
    await ElMessageBox.confirm('切换账号需要退出当前登录，是否继续？', '切换账号', { confirmButtonText: '继续', cancelButtonText: '取消', type: 'warning' })
    await handleLogout()
  } catch { /* User cancelled. */ }
}
function logoutFromMenu() { accountMenuVisible.value = false; handleLogout() }
</script>

<style scoped lang="scss">
.app-sidebar { height: 100%; display: flex; flex-direction: column; background: #faf9fc; }
.sidebar-header { height: 88px; padding: 0 16px; display: flex; align-items: center; gap: 10px; }
.sidebar-header.compact { justify-content: center; padding: 0; }
.logo { width: 76px; height: 76px; flex: 0 0 76px; object-fit: contain; animation: logo-float 4s ease-in-out infinite; }
.sidebar-header.compact .logo { width: 46px; height: 46px; flex-basis: 46px; }
.app-title { color: var(--ink-900); font-size: 18px; font-weight: 700; letter-spacing: .01em; white-space: nowrap; }
.group-label { padding: 12px 18px 8px; color: #9a94a5; font-size: 13px; font-weight: 500; }
.sidebar-menu { flex: 1; padding: 5px 10px; border-right: 0; background: transparent; }
:deep(.el-menu-item) { position: relative; height: 46px; margin-bottom: 5px; border-radius: 12px; color: var(--ink-600); font-size: 14px; transition: color .2s ease, background-color .2s ease, transform .2s ease, box-shadow .2s ease; }
:deep(.el-menu-item .el-icon) { width: 24px; margin-right: 12px; font-size: 22px; transition: transform .22s ease, color .22s ease; }
:deep(.el-menu--collapse .el-menu-item .el-icon) { margin-right: 0; }
:deep(.el-menu-item::before) { content: ''; position: absolute; left: 0; top: 12px; bottom: 12px; width: 3px; border-radius: 0 3px 3px 0; background: var(--brand-600); opacity: 0; transform: scaleY(.35); transition: opacity .2s ease, transform .2s ease; }
:deep(.el-menu-item:hover) { color: var(--brand-700); background: var(--brand-50); transform: translateX(3px); }
:deep(.el-menu-item:hover .el-icon) { color: var(--brand-600); transform: scale(1.12); }
:deep(.el-menu-item.is-active) { color: var(--brand-700); background: var(--brand-100); font-weight: 600; box-shadow: 0 5px 16px rgba(101, 70, 202, .08); }
:deep(.el-menu-item.is-active::before) { opacity: 1; transform: scaleY(1); }
:deep(.el-menu-item.is-active .el-icon) { color: var(--brand-600); animation: icon-arrive .35s ease both; }
.account-trigger { width: calc(100% - 20px); min-height: 54px; margin: 0 10px 10px; padding: 8px 10px; display: flex; align-items: center; gap: 10px; border: 1px solid transparent; border-radius: 12px; color: var(--ink-600); background: #f2f3f5; cursor: pointer; text-align: left; }
.account-trigger:hover, .account-trigger.active { border-color: var(--brand-500); box-shadow: 0 0 0 2px var(--brand-100); }
.account-trigger.compact { width: 48px; justify-content: center; margin-inline: 8px; padding: 7px; }
.account-trigger :deep(.el-avatar) { flex: 0 0 auto; color: var(--brand-700); background: var(--brand-100); font-weight: 700; }
.account-name { min-width: 0; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; font-weight: 600; }
.more { flex: 0 0 auto; color: #8d8994; }
.account-menu { display: grid; }
.menu-group { padding: 5px 0; border-bottom: 1px solid #e5e5e7; }
.menu-group:first-child { padding-top: 0; }
.menu-group:last-child { padding-bottom: 0; border-bottom: 0; }
.account-menu button { width: 100%; min-height: 42px; padding: 8px 10px; display: flex; align-items: center; gap: 10px; border: 0; border-radius: 6px; color: var(--ink-900); background: transparent; cursor: pointer; font-size: 14px; text-align: left; }
.account-menu button:hover { background: #f3f4f6; }
.account-menu button span { flex: 1; }
.account-menu .menu-arrow { margin-left: auto; color: #a09ca7; font-size: 13px; }

@keyframes logo-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-2px); } }
@keyframes icon-arrive { from { transform: scale(.86); opacity: .55; } to { transform: scale(1); opacity: 1; } }
@keyframes status-pulse { 0% { box-shadow: 0 0 0 0 rgba(88, 184, 140, .35); } 70%, 100% { box-shadow: 0 0 0 6px rgba(88, 184, 140, 0); } }

@media (prefers-reduced-motion: reduce) {
  .logo, :deep(.el-menu-item.is-active .el-icon) { animation: none; }
  :deep(.el-menu-item), :deep(.el-menu-item .el-icon) { transition: none; }
}
</style>
