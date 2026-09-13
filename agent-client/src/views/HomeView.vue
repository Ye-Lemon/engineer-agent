<template>
  <section class="workspace">
    <div class="workspace-layout">
    <div class="workspace-inner">
      <div class="eyebrow"><span class="pulse"></span> 工程知识工作台</div>
      <h1>你好，{{ displayName }}</h1>
      <p class="intro">从项目资料中获取可靠答案，整理工程文档，快速生成专业报告。</p>

      <form class="prompt-box" @submit.prevent="submitPrompt">
        <textarea v-model="prompt" :placeholder="placeholder" rows="3" aria-label="输入任务" @keydown.enter.exact.prevent="submitPrompt"></textarea>
        <input ref="fileInput" class="file-input" type="file" accept=".pdf,.doc,.docx,.txt" @change="handleFileSelected" />
        <div v-if="uploadStatus" class="upload-chip" :class="{ success: uploadStatus === 'completed', error: uploadStatus === 'failed' }">
          <el-icon><Paperclip /></el-icon><span>{{ uploadMessage }}</span><button type="button" @click="clearUploadStatus">×</button>
        </div>
        <div class="prompt-actions">
          <div class="tools">
            <button type="button" title="上传参考文件" :disabled="uploading" @click="openFilePicker"><el-icon><Paperclip /></el-icon></button>
            <span>支持引用知识空间中的文档</span>
          </div>
          <button class="send" type="submit" :disabled="!prompt.trim()" title="发送任务"><el-icon><Promotion /></el-icon></button>
        </div>
      </form>

      <div class="quick-section">
        <div class="section-heading"><span>常用任务</span><small>{{ documentCount }} 份资料已就绪</small></div>
        <div class="quick-grid">
          <button v-for="item in quickTasks" :key="item.title" type="button" @click="openTask(item)">
            <span class="task-icon"><el-icon><component :is="item.icon" /></el-icon></span>
            <span><strong>{{ item.title }}</strong><small>{{ item.description }}</small></span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
    </div>
    <aside class="history-panel">
      <button type="button" class="new-chat" @click="startNewChat"><el-icon><Plus /></el-icon><span>开启新对话</span></button>
      <div class="history-toolbar"><span>会话历史</span><button v-if="history.length" type="button" class="clear-history" @click="clearHistory">清空</button></div>
      <div v-if="history.length" class="history-list">
        <div v-for="group in historyGroups" :key="group.label" class="history-group">
          <div class="history-group-title">{{ group.label }}</div>
          <button v-for="item in group.items" :key="item.id" type="button" class="history-item" :class="{ selected: item.id === selectedHistoryId }" @click="restoreHistory(item)"><span class="history-copy"><strong>{{ item.title }}</strong><small>{{ item.time }}</small></span><span class="history-more">•••</span></button>
        </div>
      </div>
      <div v-else class="history-empty"><el-icon><ChatDotRound /></el-icon><p>发送一个任务后<br />会话会显示在这里</p></div>
      <div class="history-account"><el-avatar :size="34">{{ displayName.charAt(0).toUpperCase() }}</el-avatar><span>{{ displayName }}</span><span class="history-more">•••</span></div>
    </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Document, Folder, Paperclip, Promotion, ArrowRight, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { uploadDocument, getTaskStatus } from '@/api/upload'
import { useTaskPolling } from '@/composables/useTaskPolling'

type QuickTask = { title: string; description: string; icon: Component; prompt: string }
type HistoryItem = { id: number; title: string; time: string }
const authStore = useAuthStore()
const router = useRouter()
const prompt = ref('')
const history = ref<HistoryItem[]>([])
const selectedHistoryId = ref<number | null>(null)
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const uploadStatus = ref('')
const uploadMessage = ref('')
const { startPolling } = useTaskPolling()
const quickTasks: QuickTask[] = [
  { title: '查询工程规范', description: '基于已上传资料精准检索', icon: ChatDotRound, prompt: '请帮我查询相关工程规范：' },
  { title: '整理项目文档', description: '查看并管理知识空间', icon: Folder, prompt: '请帮我整理项目文档：' },
  { title: '生成工程报告', description: '根据资料快速形成报告', icon: Document, prompt: '请根据项目资料生成工程报告：' },
]
const displayName = computed(() => authStore.user?.username || '工程师')
const documentCount = computed(() => 0)
const placeholder = '描述你的任务，Agent 会帮你检索资料、整理文档或生成报告…'
function submitPrompt() { const text = prompt.value.trim(); if (!text) return; addHistory(text); sessionStorage.setItem('pendingPrompt', text); router.push('/query') }
function openTask(item: QuickTask) { prompt.value = item.prompt }
function addHistory(text: string) { history.value = [{ id: Date.now(), title: text, time: '刚刚' }, ...history.value.filter((item) => item.title !== text)].slice(0, 12); localStorage.setItem('workspace-history', JSON.stringify(history.value)) }
function restoreHistory(item: HistoryItem) { selectedHistoryId.value = item.id; prompt.value = item.title }
function startNewChat() { prompt.value = ''; selectedHistoryId.value = null }
function clearHistory() { history.value = []; localStorage.removeItem('workspace-history') }
function openFilePicker() { fileInput.value?.click() }
function clearUploadStatus() { uploadStatus.value = ''; uploadMessage.value = '' }
async function handleFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (file.size > 100 * 1024 * 1024) { uploadStatus.value = 'failed'; uploadMessage.value = '文件不能超过 100MB'; return }
  uploading.value = true; uploadStatus.value = 'uploading'; uploadMessage.value = `正在上传「${file.name}」…`
  try {
    const result = await uploadDocument(file)
    startPolling(async () => {
      const status = await getTaskStatus(result.task_id)
      return { status: status.status, error: status.error }
    }, () => { uploading.value = false; uploadStatus.value = 'completed'; uploadMessage.value = `「${file.name}」已上传并完成索引` })
  } catch (error: any) {
    console.error('Document upload failed:', error)
    uploading.value = false; uploadStatus.value = 'failed'; uploadMessage.value = '上传失败'
  }
}
onMounted(() => { try { history.value = JSON.parse(localStorage.getItem('workspace-history') || '[]') } catch { history.value = [] } })
const historyGroups = computed(() => [{ label: '今天', items: history.value.slice(0, 3) }, { label: '7 天内', items: history.value.slice(3, 8) }, { label: '30 天内', items: history.value.slice(8) }].filter((group) => group.items.length))
</script>

<style scoped lang="scss">
.workspace { min-height: 100%; display: grid; place-items: center; padding: 40px 34px 60px; background: radial-gradient(circle at 50% 36%, #faf8ff 0, #fff 46%); }
.workspace-layout { width: min(1240px, 100%); display: grid; grid-template-columns: minmax(0, 1fr) 292px; gap: 30px; align-items: stretch; }
.workspace-inner { width: 100%; animation: workspaceEnter .45s cubic-bezier(.22, 1, .36, 1) both; }
.history-panel { position: sticky; top: 20px; min-height: min(690px, calc(100vh - 72px)); max-height: calc(100vh - 72px); padding: 22px 14px 14px; border: 1px solid #e8e3f0; border-radius: 18px; background: #f7f8fa; box-shadow: 0 14px 36px rgba(71,51,117,.08); overflow: auto; display: flex; flex-direction: column; }
.new-chat { width: 100%; height: 48px; display: flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid #e2e5eb; border-radius: 24px; color: #30343b; background: #fff; cursor: pointer; font-size: 14px; box-shadow: 0 2px 5px rgba(31,35,41,.05); }
.new-chat:hover { border-color: var(--brand-300); color: var(--brand-700); }
.history-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 32px 10px 12px; color: #8b9099; font-size: 13px; }
.clear-history { padding: 4px 6px; border: 0; border-radius: 7px; color: #9b94a6; background: transparent; cursor: pointer; font-size: 12px; }
.clear-history:hover { color: var(--brand-600); }
.history-list { display: grid; gap: 16px; }
.history-group { display: grid; gap: 3px; }
.history-group-title { padding: 0 10px 5px; color: #9aa0aa; font-size: 12px; }
.history-item { display: flex; align-items: center; width: 100%; min-width: 0; min-height: 46px; padding: 10px 10px; border: 0; border-radius: 10px; color: #252932; background: transparent; text-align: left; cursor: pointer; }
.history-item:hover, .history-item.selected { background: #e3edff; color: #356bea; }
.history-item.selected { box-shadow: inset 3px 0 0 #4c7dff; }
.history-more { margin-left: auto; padding-left: 6px; color: #8f96a0; letter-spacing: 2px; opacity: 0; }
.history-item:hover .history-more, .history-item.selected .history-more { opacity: 1; }
.history-copy { min-width: 0; }
.history-copy strong, .history-copy small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-copy strong { font-size: 13px; font-weight: 600; }
.history-copy small { margin-top: 4px; color: #aaa4b2; font-size: 11px; }
.history-empty { display: grid; place-items: center; gap: 9px; padding: 100px 8px; color: #b2acba; text-align: center; }
.history-empty .el-icon { font-size: 25px; color: #c9c2d4; }
.history-empty p { font-size: 12px; line-height: 1.6; }
.history-account { display: flex; align-items: center; gap: 10px; margin: auto 4px 0; padding: 14px 8px 4px; border-top: 1px solid #e2e5eb; color: #686f79; font-size: 13px; }
.history-account .history-more { opacity: 1; }
.eyebrow { display: flex; align-items: center; gap: 9px; color: var(--brand-600); font-size: 14px; font-weight: 600; }
.pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--brand-500); box-shadow: 0 0 0 4px var(--brand-100); }
h1 { margin: 16px 0 8px; font-size: 44px; line-height: 1.2; letter-spacing: 0; font-weight: 700; }
.intro { color: var(--ink-600); font-size: 16px; line-height: 1.7; }
.mode-switch { display: none; }
.mode-switch button { min-height: 42px; display: flex; align-items: center; gap: 7px; padding: 9px 14px; border: 1px solid var(--line); border-radius: 11px; color: var(--ink-600); background: #fff; cursor: pointer; font-size: 14px; }
.mode-switch button.active { color: var(--brand-700); border-color: var(--brand-200); background: var(--brand-50); }
.prompt-box { border: 1px solid #ded9e8; border-radius: 16px; background: #fff; box-shadow: 0 16px 44px rgba(71, 51, 117, .10); overflow: hidden; }
.file-input { display: none; }
.upload-chip { display: inline-flex; align-items: center; gap: 7px; max-width: min(360px, calc(100% - 40px)); margin: 0 20px 10px; padding: 6px 9px; border: 1px solid #ddd2ff; border-radius: 9px; color: var(--brand-700); background: var(--brand-50); font-size: 12px; line-height: 1.35; vertical-align: top; }
.upload-chip.success { color: #237a57; border-color: #b8e6d2; background: #f0fbf6; }
.upload-chip.error { color: #b34b58; border-color: #f2c9cf; background: #fff5f6; }
.upload-chip span { min-width: 0; max-width: 290px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.upload-chip button { flex: 0 0 auto; width: 18px; height: 18px; padding: 0; border: 0; border-radius: 50%; color: inherit; background: transparent; cursor: pointer; font-size: 16px; line-height: 16px; }
.upload-chip button:hover { background: rgba(117,87,217,.12); }
textarea { display: block; width: 100%; min-height: 142px; padding: 22px 24px; border: 0; outline: 0; resize: none; color: var(--ink-900); background: transparent; font-size: 16px; line-height: 1.6; }
textarea::placeholder { color: #a29daa; }
.prompt-actions { min-height: 58px; padding: 9px 11px 9px 18px; border-top: 1px solid #f0edf4; display: flex; align-items: center; justify-content: space-between; }
.tools { display: flex; align-items: center; gap: 9px; color: #9993a2; font-size: 12px; }
.tools button, .send { width: 38px; height: 38px; border: 0; border-radius: 6px; display: grid; place-items: center; cursor: pointer; }
.tools button { color: var(--ink-600); background: transparent; }
.tools button:nth-of-type(2) { display: none; }
.tools button:disabled { cursor: wait; opacity: .45; }
.tools button:hover { background: var(--brand-50); color: var(--brand-600); }
.send { color: white; background: var(--brand-600); }
.send:disabled { cursor: default; opacity: .35; }
.quick-section { margin-top: 42px; }
.section-heading { display: flex; justify-content: space-between; margin-bottom: 14px; font-size: 14px; font-weight: 600; }
.section-heading small { color: #aaa4b2; font-weight: 400; }
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quick-grid > button { min-width: 0; min-height: 78px; display: grid; grid-template-columns: 42px 1fr 18px; align-items: center; gap: 12px; padding: 16px; text-align: left; border: 1px solid var(--line); border-radius: 14px; background: #fff; cursor: pointer; transition: border-color .18s, background .18s, transform .18s, box-shadow .18s; }
.quick-grid > button:hover { border-color: var(--brand-200); background: var(--brand-50); }
.quick-grid > button:hover { transform: translateY(-3px); box-shadow: var(--shadow-soft); }
.task-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 6px; color: var(--brand-600); background: var(--brand-100); font-size: 18px; }
.quick-grid strong, .quick-grid small { display: block; overflow-wrap: anywhere; }
.quick-grid strong { margin-bottom: 5px; color: var(--ink-900); font-size: 14px; }
.quick-grid small { color: #918b99; font-size: 12px; line-height: 1.4; }
.arrow { color: #aaa4b2; }
@keyframes workspaceEnter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .workspace-inner { animation: none; } .quick-grid > button { transition: none; } }
@media (max-width: 960px) { .workspace-layout { grid-template-columns: minmax(0, 1fr) 260px; gap: 18px; } }
@media (max-width: 760px) { .workspace { place-items: start center; padding: 28px 16px 40px; } .workspace-layout { grid-template-columns: 1fr; } .history-panel { position: static; min-height: 0; } .history-empty { padding: 30px 8px; } h1 { font-size: 34px; } .quick-grid { grid-template-columns: 1fr; } .mode-switch { overflow-x: auto; } .mode-switch button { flex: 0 0 auto; } .tools span { display: none; } }
</style>
