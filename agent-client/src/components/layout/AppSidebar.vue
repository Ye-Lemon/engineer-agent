<template>
  <div class="app-sidebar">
    <div class="sidebar-header"><img src="@/assets/logo.svg" class="logo" alt="Logo" /><span v-if="!collapsed" class="app-title">工程助手</span></div>
    <div v-if="!collapsed" class="group-label">工作空间</div>
    <el-menu :default-active="route.path" :collapse="collapsed" router class="sidebar-menu"><el-menu-item v-for="item in items" :key="item.path" :index="item.path"><el-icon><component :is="item.icon" /></el-icon><template #title>{{ item.label }}</template></el-menu-item></el-menu>
    <section v-if="!collapsed" class="sidebar-history">
      <button class="new-chat" type="button" @click="startNewChat"><el-icon><Plus /></el-icon>开启新对话</button>
      <div class="history-toolbar"><span>会话历史</span><button v-if="history.length" class="history-clear" type="button" @click="clearHistory">清空</button></div>
      <div v-if="history.length" class="history-list"><div v-for="group in historyGroups" :key="group.label"><div class="history-group-title">{{ group.label }}</div><button v-for="item in group.items" :key="item.id" class="history-row" :class="{ selected: item.id === selectedHistoryId }" type="button" @click="openHistory(item)"><el-icon><ChatDotRound /></el-icon><span>{{ item.title }}</span></button></div></div>
      <div v-else class="history-empty"><el-icon><ChatDotRound /></el-icon><span>发送一个任务后<br />会话会显示在这里</span></div>
    </section>
    <div v-if="!collapsed && accountMenuOpen" class="account-menu"><button type="button"><el-icon><Iphone /></el-icon>下载手机应用</button><button type="button" @click="settingsVisible = true"><el-icon><Setting /></el-icon>系统设置</button><button type="button"><el-icon><QuestionFilled /></el-icon>帮助与反馈</button><button type="button" @click="logout"><el-icon><SwitchButton /></el-icon>退出登录</button></div>
    <button class="account-trigger" type="button" @click="accountMenuOpen = !accountMenuOpen"><el-avatar :size="38">{{ initial }}</el-avatar><span v-if="!collapsed" class="account-name">{{ username }}</span></button>
    <el-dialog v-model="settingsVisible" title="系统设置" width="680px"><div class="settings-placeholder">设置中心</div></el-dialog>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound, Document, Folder, HomeFilled, Iphone, Plus, QuestionFilled, Setting, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
defineProps<{ collapsed: boolean }>()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const username = computed(() => auth.user?.username || '用户')
const initial = computed(() => username.value.charAt(0).toUpperCase())
const history = ref<{ id: number; title: string; time: string }[]>([])
const selectedHistoryId = ref<number | null>(null)
const accountMenuOpen = ref(false)
const settingsVisible = ref(false)
const items = [{ path: '/', label: '工作台', icon: HomeFilled }, { path: '/files', label: '知识空间', icon: Folder }, { path: '/report', label: '报告生成', icon: Document }]
const historyGroups = computed(() => [{ label: '今天', items: history.value.slice(0, 3) }, { label: '7 天内', items: history.value.slice(3, 8) }, { label: '30 天内', items: history.value.slice(8) }].filter((group) => group.items.length))
function startNewChat() { selectedHistoryId.value = null; router.push('/') }
function openHistory(item: { id: number; title: string }) { selectedHistoryId.value = item.id; sessionStorage.setItem('pendingConversationId', String(item.id)); sessionStorage.setItem('pendingPrompt', item.title); router.push({ path: '/query', query: { conversation: String(item.id) } }) }
function clearHistory() { history.value = []; localStorage.removeItem('workspace-history') }
async function logout() { accountMenuOpen.value = false; await auth.logout(); router.push('/login') }
function loadHistory() { try { history.value = JSON.parse(localStorage.getItem('workspace-history') || '[]') } catch { history.value = [] } }
onMounted(() => { loadHistory(); window.addEventListener('workspace-history-updated', loadHistory) })
</script>
<style scoped lang="scss">
.app-sidebar{height:100%;display:flex;flex-direction:column;background:#faf9fc}.sidebar-header{height:88px;padding:0 18px;display:flex;align-items:center;gap:11px}.logo{width:58px;height:58px}.app-title{font-size:20px;font-weight:700}.group-label{padding:14px 20px 9px;color:#9a94a5;font-size:16px}.sidebar-menu{flex:0 0 auto;padding:6px 10px;border:0;background:transparent}.sidebar-menu :deep(.el-menu-item){height:52px;line-height:52px;font-size:17px}.sidebar-menu :deep(.el-menu-item .el-icon){width:22px;height:22px;margin-right:10px;font-size:21px}.sidebar-history{min-height:0;flex:1;display:flex;flex-direction:column;margin:8px 10px 12px;padding:12px 8px;border-top:1px solid #e9e6ef;overflow:hidden}.new-chat{height:48px;border:1px solid #e2e5eb;border-radius:12px;background:#fff;font-size:16px;cursor:pointer}.history-toolbar{display:flex;justify-content:space-between;padding:16px 6px 8px;color:#8b9099;font-size:15px}.history-clear{border:0;background:transparent;color:#9b94a6;cursor:pointer}.history-list{flex:1;overflow:auto;display:grid;align-content:start;gap:14px}.history-list>div{display:flex;flex-direction:column}.history-group-title{padding:0 6px 4px;color:#9aa0aa;font-size:14px}.history-row{display:flex;align-items:center;gap:8px;width:100%;min-height:44px;padding:8px;border:0;border-radius:9px;background:transparent;text-align:left;cursor:pointer}.history-row span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:16px}.history-row:hover,.history-row.selected{color:#356bea;background:#e3edff}.history-empty{flex:1;display:grid;place-items:center;text-align:center;color:#afb4bd;font-size:14px}.account-trigger{width:calc(100% - 20px);min-height:60px;margin:0 10px 10px;padding:8px 10px;display:flex;align-items:center;gap:10px;border:0;border-radius:12px;background:#f2f3f5;text-align:left}.account-name{font-size:16px;font-weight:600}
.app-sidebar{height:100%;display:flex;flex-direction:column;background:#faf9fc}.sidebar-header{height:88px;padding:0 18px;display:flex;align-items:center;gap:11px}.logo{width:58px;height:58px}.app-title{font-size:20px;font-weight:700}.group-label{padding:14px 20px 9px;color:#9a94a5;font-size:16px}.sidebar-menu{flex:0 0 auto;padding:6px 10px;border:0;background:transparent}.sidebar-menu :deep(.el-menu-item){height:52px;line-height:52px;font-size:17px}.sidebar-menu :deep(.el-menu-item .el-icon){width:22px;height:22px;margin-right:10px;font-size:21px}.sidebar-history{min-height:0;flex:1;display:flex;flex-direction:column;margin:8px 10px 12px;padding:12px 8px;border-top:1px solid #e9e6ef;overflow:hidden}.new-chat{height:48px;border:1px solid #e2e5eb;border-radius:12px;background:#fff;font-size:16px;cursor:pointer}.history-toolbar{display:flex;justify-content:space-between;padding:16px 6px 8px;color:#8b9099;font-size:15px}.history-clear{border:0;background:transparent;color:#9b94a6;cursor:pointer}.history-list{flex:1;overflow:auto;display:grid;align-content:start;gap:14px}.history-list>div{display:flex;flex-direction:column}.history-group-title{padding:0 6px 4px;color:#9aa0aa;font-size:14px}.history-row{display:flex;align-items:center;gap:8px;width:100%;min-height:44px;padding:8px;border:0;border-radius:9px;background:transparent;text-align:left;cursor:pointer}.history-row span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:16px}.history-row:hover,.history-row.selected{color:#356bea;background:#e3edff}.history-empty{flex:1;display:grid;place-items:center;text-align:center;color:#afb4bd;font-size:14px}.account-menu{margin:0 10px 8px;padding:8px;border:1px solid #e2e5eb;border-radius:12px;background:#fff;box-shadow:0 8px 20px rgba(40,45,60,.12)}.account-menu button{width:100%;height:42px;display:flex;align-items:center;gap:10px;padding:0 10px;border:0;border-radius:8px;background:transparent;text-align:left;font-size:15px;cursor:pointer}.account-menu button:hover{background:#f0f3f8}.account-trigger{width:calc(100% - 20px);min-height:60px;margin:0 10px 10px;padding:8px 10px;display:flex;align-items:center;gap:10px;border:0;border-radius:12px;background:#f2f3f5;text-align:left}.account-name{font-size:16px;font-weight:600}.settings-placeholder{padding:30px;text-align:center;color:#7a8190}
</style>
