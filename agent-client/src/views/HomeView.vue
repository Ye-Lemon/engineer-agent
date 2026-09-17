<template>
  <section class="workspace">
    <div class="workspace-inner">
      <div class="eyebrow"><span class="pulse" /> 工程知识工作台</div>
      <h1>你好，{{ displayName }}</h1>
      <p class="intro">从项目资料中获取可靠答案，整理工程文档，快速生成专业报告。</p>
      <form class="prompt-box" @submit.prevent="submitPrompt">
        <textarea v-model="prompt" rows="3" placeholder="描述你的任务，Agent 会帮你检索资料、整理文档或生成报告…" aria-label="输入任务" @keydown.enter.exact.prevent="submitPrompt" />
        <input ref="fileInput" class="file-input" type="file" accept=".pdf,.doc,.docx,.txt" @change="handleFileSelected" />
        <div class="prompt-actions">
          <div class="tools"><button type="button" title="上传参考文件" :disabled="uploading" @click="openFilePicker"><el-icon><Paperclip /></el-icon></button><span>支持引用知识空间中的文档</span></div>
          <div class="actions-right"><el-dropdown trigger="click" @command="selectModel"><button class="model-picker" type="button" aria-label="选择模型">{{ selectedModelLabel }}<el-icon><ArrowDown /></el-icon></button><template #dropdown><el-dropdown-menu><el-dropdown-item v-for="model in modelOptions" :key="model.value" :command="model.value">{{ model.label }}</el-dropdown-item></el-dropdown-menu></template></el-dropdown><button class="send" type="submit" :disabled="!prompt.trim()" title="发送任务"><el-icon><Promotion /></el-icon></button></div>
        </div>
      </form>
    </div>
  </section>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDown, Paperclip, Promotion } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { uploadDocument, getTaskStatus } from '@/api/upload'
import { useTaskPolling } from '@/composables/useTaskPolling'
const authStore = useAuthStore()
const router = useRouter()
const prompt = ref('')
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const modelOptions = [{ label: 'DeepSeek V3.2', value: 'deepseek-v3.2' }, { label: 'GPT-4o', value: 'gpt-4o' }, { label: '5.6 Sol', value: '5.6-sol' }]
const selectedModel = ref(localStorage.getItem('workspace-model') || 'deepseek-v3.2')
const displayName = computed(() => authStore.user?.username || '工程师')
const selectedModelLabel = computed(() => modelOptions.find((model) => model.value === selectedModel.value)?.label || 'DeepSeek V3.2')
const { startPolling } = useTaskPolling()
function submitPrompt() { const text = prompt.value.trim(); if (!text) return; let history: Array<{ id: number; title: string; time: string }> = []; try { history = JSON.parse(localStorage.getItem('workspace-history') || '[]') } catch { history = [] }; localStorage.setItem('workspace-history', JSON.stringify([{ id: Date.now(), title: text, time: '刚刚' }, ...history.filter((item) => item.title !== text)].slice(0, 12))); localStorage.setItem('workspace-model', selectedModel.value); sessionStorage.setItem('pendingPrompt', text); sessionStorage.setItem('pendingModel', selectedModel.value); router.push('/query') }
function selectModel(value: string) { selectedModel.value = value }
function openFilePicker() { fileInput.value?.click() }
async function handleFileSelected(event: Event) { const input = event.target as HTMLInputElement; const file = input.files?.[0]; input.value = ''; if (!file) return; if (file.size > 100 * 1024 * 1024) return; uploading.value = true; try { const result = await uploadDocument(file); startPolling(async () => { const status = await getTaskStatus(result.task_id); return { status: status.status, error: status.error } }, () => { uploading.value = false }) } catch { uploading.value = false } }
</script>
<style scoped lang="scss">
.workspace{min-height:100%;display:grid;place-items:center;padding:40px 34px 60px;background:#fff}.workspace-inner{width:min(880px,100%)}.eyebrow{color:var(--brand-600);font-weight:600;font-size:17px}.pulse{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--brand-500)}h1{margin:16px 0 8px;font-size:46px}.intro{margin:18px 0 26px;color:var(--ink-600);font-size:18px}.prompt-box{border:1px solid #ded9e8;border-radius:18px;background:#fff;overflow:hidden}.file-input{display:none}textarea{display:block;width:100%;min-height:150px;padding:24px;border:0;outline:0;resize:none;font-size:18px}.prompt-actions{min-height:66px;padding:10px 14px 10px 20px;border-top:1px solid #f0edf4;display:flex;align-items:center;justify-content:space-between}.tools,.actions-right{display:flex;align-items:center}.tools{gap:10px;color:#9993a2;font-size:16px}.tools button{width:42px;height:42px;border:0;border-radius:10px;background:transparent;display:grid;place-items:center;cursor:pointer;font-size:22px}.actions-right{gap:12px}.model-picker{display:flex;align-items:center;gap:5px;padding:0;border:0;outline:0;background:transparent;box-shadow:none;color:#586170;font-size:16px;cursor:pointer}.model-picker .el-icon{font-size:15px}.send{width:46px;height:46px;border:0;border-radius:50%;color:#fff;background:#b7adf0;display:grid;place-items:center;font-size:22px}.send:disabled{opacity:.35}@media(max-width:760px){.workspace{padding:28px 16px 40px}h1{font-size:36px}.tools span{display:none}}
</style>
