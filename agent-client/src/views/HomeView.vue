<template>
  <section class="workspace">
    <div class="workspace-inner">
      <div class="eyebrow"><span class="pulse"></span> 工程知识工作台</div>
      <h1>你好，{{ displayName }}</h1>
      <p class="intro">从项目资料中获取可靠答案，整理工程文档，快速生成专业报告。</p>

      <div class="mode-switch" aria-label="工作模式">
        <button v-for="mode in modes" :key="mode.label" :class="{ active: activeMode === mode.key }" @click="selectMode(mode)">
          <el-icon><component :is="mode.icon" /></el-icon>{{ mode.label }}
        </button>
      </div>

      <form class="prompt-box" @submit.prevent="submitPrompt">
        <textarea v-model="prompt" :placeholder="placeholder" rows="3" aria-label="输入任务"></textarea>
        <div class="prompt-actions">
          <div class="tools">
            <button type="button" title="上传参考文件" @click="router.push('/upload')"><el-icon><Paperclip /></el-icon></button>
            <span>支持引用知识空间中的文档</span>
          </div>
          <button class="send" type="submit" :disabled="!prompt.trim()" title="发送"><el-icon><Promotion /></el-icon></button>
        </div>
      </form>

      <div class="quick-section">
        <div class="section-heading"><span>常用任务</span><small>{{ documentCount }} 份资料已就绪</small></div>
        <div class="quick-grid">
          <button v-for="item in quickTasks" :key="item.title" @click="openTask(item)">
            <span class="task-icon"><el-icon><component :is="item.icon" /></el-icon></span>
            <span><strong>{{ item.title }}</strong><small>{{ item.description }}</small></span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Document, Folder, Upload, Paperclip, Promotion, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

type WorkItem = { key: string; label: string; route: string; icon: Component; placeholder: string }
type QuickTask = { title: string; description: string; route: string; icon: Component; prompt?: string }
const router = useRouter()
const authStore = useAuthStore()
const prompt = ref('')
const activeMode = ref('query')
const modes: WorkItem[] = [
  { key: 'query', label: '智能问答', route: '/query', icon: ChatDotRound, placeholder: '询问施工规范、项目资料或技术问题…' },
  { key: 'report', label: '生成报告', route: '/report', icon: Document, placeholder: '描述需要生成的报告主题和要求…' },
  { key: 'upload', label: '上传资料', route: '/upload', icon: Upload, placeholder: '前往上传工程资料并建立知识库…' },
]
const quickTasks: QuickTask[] = [
  { title: '查询工程规范', description: '基于已上传资料精准检索', route: '/query', icon: ChatDotRound, prompt: '请帮我查询相关工程规范：' },
  { title: '整理项目文档', description: '查看并管理知识空间', route: '/files', icon: Folder },
  { title: '生成工程报告', description: '根据资料快速形成报告', route: '/report', icon: Document },
]
const displayName = computed(() => authStore.user?.username || '工程师')
const documentCount = computed(() => 0)
const currentMode = computed(() => modes.find((item) => item.key === activeMode.value) || modes[0])
const placeholder = computed(() => currentMode.value.placeholder)
function selectMode(mode: WorkItem) { activeMode.value = mode.key; if (mode.key === 'upload') router.push(mode.route) }
function submitPrompt() { if (!prompt.value.trim()) return; sessionStorage.setItem('pendingPrompt', prompt.value.trim()); router.push(currentMode.value.route) }
function openTask(item: QuickTask) { if (item.prompt) sessionStorage.setItem('pendingPrompt', item.prompt); router.push(item.route) }
</script>

<style scoped lang="scss">
.workspace { min-height: 100%; display: grid; place-items: center; padding: 48px 40px 68px; background: radial-gradient(circle at 50% 36%, #faf8ff 0, #fff 46%); }
.workspace-inner { width: min(900px, 100%); }
.eyebrow { display: flex; align-items: center; gap: 9px; color: var(--brand-600); font-size: 14px; font-weight: 600; }
.pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--brand-500); box-shadow: 0 0 0 4px var(--brand-100); }
h1 { margin: 16px 0 8px; font-size: clamp(36px, 5vw, 48px); line-height: 1.18; letter-spacing: 0; }
.intro { color: var(--ink-600); font-size: 16px; line-height: 1.7; }
.mode-switch { display: flex; gap: 8px; margin: 34px 0 12px; }
.mode-switch button { min-height: 42px; display: flex; align-items: center; gap: 7px; padding: 9px 14px; border: 1px solid var(--line); border-radius: 6px; color: var(--ink-600); background: #fff; cursor: pointer; font-size: 14px; }
.mode-switch button.active { color: var(--brand-700); border-color: var(--brand-200); background: var(--brand-50); }
.prompt-box { border: 1px solid #ded9e8; border-radius: 8px; background: #fff; box-shadow: 0 16px 44px rgba(71, 51, 117, .10); overflow: hidden; }
textarea { display: block; width: 100%; min-height: 142px; padding: 22px 24px; border: 0; outline: 0; resize: none; color: var(--ink-900); background: transparent; font-size: 16px; line-height: 1.6; }
textarea::placeholder { color: #a29daa; }
.prompt-actions { min-height: 58px; padding: 9px 11px 9px 18px; border-top: 1px solid #f0edf4; display: flex; align-items: center; justify-content: space-between; }
.tools { display: flex; align-items: center; gap: 9px; color: #9993a2; font-size: 12px; }
.tools button, .send { width: 38px; height: 38px; border: 0; border-radius: 6px; display: grid; place-items: center; cursor: pointer; }
.tools button { color: var(--ink-600); background: transparent; }
.tools button:hover { background: var(--brand-50); color: var(--brand-600); }
.send { color: white; background: var(--brand-600); }
.send:disabled { cursor: default; opacity: .35; }
.quick-section { margin-top: 42px; }
.section-heading { display: flex; justify-content: space-between; margin-bottom: 14px; font-size: 14px; font-weight: 600; }
.section-heading small { color: #aaa4b2; font-weight: 400; }
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quick-grid > button { min-width: 0; min-height: 78px; display: grid; grid-template-columns: 42px 1fr 18px; align-items: center; gap: 12px; padding: 16px; text-align: left; border: 1px solid var(--line); border-radius: 7px; background: #fff; cursor: pointer; transition: border-color .18s, background .18s; }
.quick-grid > button:hover { border-color: var(--brand-200); background: var(--brand-50); }
.task-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 6px; color: var(--brand-600); background: var(--brand-100); font-size: 18px; }
.quick-grid strong, .quick-grid small { display: block; overflow-wrap: anywhere; }
.quick-grid strong { margin-bottom: 5px; color: var(--ink-900); font-size: 14px; }
.quick-grid small { color: #918b99; font-size: 12px; line-height: 1.4; }
.arrow { color: #aaa4b2; }
@media (max-width: 720px) { .workspace { place-items: start center; padding: 40px 18px; } .quick-grid { grid-template-columns: 1fr; } .mode-switch { overflow-x: auto; } .mode-switch button { flex: 0 0 auto; } .tools span { display: none; } }
</style>
