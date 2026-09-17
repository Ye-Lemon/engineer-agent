<template>
  <div class="query-view">
    <aside v-if="messages.length > 1" class="node-selector" aria-label="会话节点">
      <button v-for="(message, index) in messages" :key="message.id" type="button" :class="{ active: index === activeNode }" :title="`第 ${index + 1} 轮对话`" @click="jumpToMessage(message.id, index)"><span>★</span></button>
    </aside>
    <main class="conversation">
      <template v-for="message in messages" :key="message.id">
        <div :id="`message-${message.id}`" class="message-block">
        <div class="user-message">
          <template v-if="message.editing"><textarea v-model="message.editText" rows="3" @keydown.enter.exact.prevent="saveEdit(message)" /><div class="edit-actions"><button type="button" @click="saveEdit(message)">发送</button><button type="button" @click="message.editing = false">取消</button></div></template>
          <template v-else><span>{{ message.question }}</span><div class="message-actions"><button title="复制" type="button"><el-icon><CopyDocument /></el-icon></button><button title="编辑" type="button" @click="startEdit(message)"><el-icon><Edit /></el-icon></button></div></template>
        </div>
        <section class="assistant-message">
          <button class="thinking-toggle" type="button" @click="message.showThinking = !message.showThinking">
            <span class="thinking-icon" aria-hidden="true"><i class="pad pad-main" /><i class="pad pad-left" /><i class="pad pad-right" /><i class="pad pad-top" /></span>
            <span>{{ message.loading ? '正在推理…' : '已思考' }}<template v-if="!message.loading">（用时 {{ message.elapsed }} 秒）</template></span><el-icon :class="{ rotated: message.showThinking }"><ArrowDown /></el-icon>
          </button>
          <div v-if="message.showThinking" class="thinking-content">{{ message.result?.reasoning || '正在分析问题、检索知识空间并组织答案。' }}</div>
          <div v-if="!message.loading && message.result?.reasoning" class="reasoning-content">{{ message.result.reasoning }}</div>
          <div v-if="message.result" class="answer-content" v-html="renderAnswer(message.result.answer)" />
          <div v-if="message.result" class="answer-actions"><button title="复制" type="button"><el-icon><CopyDocument /></el-icon></button><button title="重新生成" type="button" @click="resend(message)"><el-icon><RefreshRight /></el-icon></button><button title="分享" type="button"><el-icon><Share /></el-icon></button></div>
        </section>
        </div>
      </template>
    </main>
    <form class="composer" @submit.prevent="submitCurrent">
      <div v-if="selectedFile" class="uploaded-file" :class="selectedFile.status"><span class="file-icon"><el-icon><Document /></el-icon></span><span class="file-meta"><strong>{{ selectedFile.name }}</strong><small>{{ selectedFile.extension }} {{ selectedFile.size }} · {{ selectedFile.status === 'uploading' ? `上传中 ${selectedFile.progress}%` : selectedFile.status === 'success' ? '上传成功' : '上传失败' }}</small><span v-if="selectedFile.status === 'uploading'" class="progress-track"><i :style="{ width: `${selectedFile.progress}%` }" /></span></span><button type="button" title="移除文件" @click="selectedFile = null">×</button></div>
      <textarea v-model="question" rows="2" placeholder="来和小P同学参与一场愉快的交流吧 ~~~" @keydown.enter.exact.prevent="submitCurrent" />
      <input ref="fileInput" class="file-input" type="file" accept=".pdf,.doc,.docx,.txt,.md,.markdown,.csv,.tsv,.json,.html,.htm,.xlsx,.xls,.pptx,.ppt" @change="handleFileSelected" />
      <div class="composer-toolbar"><button class="attach" type="button" title="上传文件" @click="openFilePicker"><el-icon><Paperclip /></el-icon></button><el-dropdown class="model-dropdown" trigger="click" @command="selectModel"><button class="model-picker" type="button">{{ modelName }}<el-icon><ArrowDown /></el-icon></button><template #dropdown><el-dropdown-menu><el-dropdown-item v-for="model in modelOptions" :key="model.id" :command="model.id">{{ model.name }}</el-dropdown-item></el-dropdown-menu></template></el-dropdown><button class="send" type="submit" :disabled="loading || !question.trim()" title="发送"><el-icon><Promotion /></el-icon></button></div>
    </form>
    <p class="disclaimer">内容由 AI 生成，请仔细甄别</p>
  </div>
</template>
<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, CopyDocument, Document, Paperclip, Promotion, RefreshRight, Share } from '@element-plus/icons-vue'
import { getChatModels, queryKnowledge as requestKnowledge } from '@/api/query'
import { useRoute } from 'vue-router'
import { uploadDocument } from '@/api/upload'
import type { QueryResponse } from '@/types'
import { marked } from 'marked'
type Message = { id: number; question: string; result: QueryResponse | null; loading: boolean; elapsed: number; showThinking: boolean; editing?: boolean; editText?: string }
const question = ref(''); const messages = ref<Message[]>([]); const loading = ref(false); const fileInput = ref<HTMLInputElement>(); const uploading = ref(false); const activeNode = ref(0)
const selectedFile = ref<{ name: string; extension: string; size: string; progress: number; status: 'uploading' | 'success' | 'error' } | null>(null)
const route = useRoute()
const sessionId = ref(sessionStorage.getItem('chat-session-id') || crypto.randomUUID())
sessionStorage.setItem('chat-session-id', sessionId.value)
async function queryKnowledge(params: { question: string; top_k: number; model: string }) {
  return requestKnowledge({ ...params, session_id: sessionId.value })
}
const modelOptions = ref([{ id: 'deepseek-v3.2', name: 'DeepSeek V3.2' }]); const selectedModel = ref(sessionStorage.getItem('pendingModel') || localStorage.getItem('workspace-model') || 'deepseek-v3.2'); const modelName = computed(() => modelOptions.value.find((model) => model.id === selectedModel.value)?.name || 'DeepSeek V3.2')
function renderAnswer(answer: string) { return marked(answer) }
function selectModel(id: string) { selectedModel.value = id; localStorage.setItem('workspace-model', id) }
function jumpToMessage(id: number, index: number) { activeNode.value = index; document.getElementById(`message-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
function submitCurrent() { if (question.value.trim()) submitMessage(question.value.trim()) }
async function submitMessage(text: string) { question.value = ''; const conversationId = Date.now(); let history: Array<{ id: number; title: string; time: string }> = []; try { history = JSON.parse(localStorage.getItem('workspace-history') || '[]') } catch { history = [] }; localStorage.setItem('workspace-history', JSON.stringify([{ id: conversationId, title: text, time: '刚刚' }, ...history.filter((item) => item.title !== text)].slice(0, 12))); window.dispatchEvent(new Event('workspace-history-updated')); const message: Message = { id: conversationId, question: text, result: null, loading: true, elapsed: 0, showThinking: true }; messages.value.push(message); activeNode.value = messages.value.length - 1; await nextTick(); jumpToMessage(conversationId, activeNode.value); loading.value = true; const started = Date.now(); try { message.result = await queryKnowledge({ question: text, top_k: 5, model: selectedModel.value }); message.elapsed = Math.max(1, Math.round((Date.now() - started) / 1000)); const saved = JSON.parse(localStorage.getItem('workspace-conversations') || '{}'); saved[conversationId] = messages.value.filter((item) => item.result).map((item) => ({ ...item, loading: false })); localStorage.setItem('workspace-conversations', JSON.stringify(saved)) } catch (error: any) { ElMessage.error(error.message || '请求失败') } finally { message.loading = false; loading.value = false } }
function resend(message: Message) { runMessage(message, message.question) }
function startEdit(message: Message) { message.editText = message.question; message.editing = true }
function saveEdit(message: Message) { const text = (message.editText || '').trim(); if (text) runMessage(message, text) }
function saveConversations(message: Message) { const saved = JSON.parse(localStorage.getItem('workspace-conversations') || '{}'); saved[message.id] = [{ ...message, loading: false }]; localStorage.setItem('workspace-conversations', JSON.stringify(saved)) }
async function runMessage(message: Message, text: string) { message.question = text; message.editing = false; message.result = null; message.loading = true; message.showThinking = true; loading.value = true; const started = Date.now(); try { message.result = await queryKnowledge({ question: text, top_k: 5, model: selectedModel.value }); message.elapsed = Math.max(1, Math.round((Date.now() - started) / 1000)); saveConversations(message) } catch (error: any) { ElMessage.error(error.message || '请求失败') } finally { message.loading = false; loading.value = false } }
function openFilePicker() { fileInput.value?.click() }
async function handleFileSelected(event: Event) { const input = event.target as HTMLInputElement; const file = input.files?.[0]; input.value = ''; if (!file || file.size > 100 * 1024 * 1024) return; const extension = file.name.includes('.') ? file.name.split('.').pop()?.toUpperCase() || 'FILE' : 'FILE'; const size = file.size < 1024 * 1024 ? `${(file.size / 1024).toFixed(1)}KB` : `${(file.size / 1024 / 1024).toFixed(2)}MB`; selectedFile.value = { name: file.name, extension, size, progress: 0, status: 'uploading' }; uploading.value = true; try { await uploadDocument(file, undefined, (progress) => { if (selectedFile.value) selectedFile.value.progress = progress }); if (selectedFile.value) { selectedFile.value.progress = 100; selectedFile.value.status = 'success' }; ElMessage.success('文件已上传') } catch (error: any) { if (selectedFile.value) selectedFile.value.status = 'error'; ElMessage.error(error.message || '上传失败') } finally { uploading.value = false } }
function loadConversation(id: string): boolean { try { const saved = JSON.parse(localStorage.getItem('workspace-conversations') || '{}')[id]; if (saved?.length) { messages.value = saved; return true } } catch { /* ignore malformed cache */ } return false }
onMounted(() => { getChatModels().then((result) => { if (result.models?.length) modelOptions.value = result.models }).catch(() => undefined); const pendingId = String(route.query.conversation || sessionStorage.getItem('pendingConversationId') || ''); const pending = sessionStorage.getItem('pendingPrompt'); if (pendingId) { loadConversation(pendingId); sessionStorage.removeItem('pendingConversationId'); sessionStorage.removeItem('pendingPrompt'); if (messages.value.length) return } if (pending) { sessionStorage.removeItem('pendingPrompt'); submitMessage(pending) } })
watch(() => route.query.conversation, (id) => { if (!id) return; const restored = loadConversation(String(id)); if (!restored) { const pending = sessionStorage.getItem('pendingPrompt'); if (pending) { sessionStorage.removeItem('pendingPrompt'); messages.value = []; submitMessage(pending) } } })
</script>
<style scoped lang="scss">
.message-block { scroll-margin-top: 72px; }
.query-view{position:relative;min-height:100%;display:flex;flex-direction:column;align-items:center;padding:34px 24px 18px;background:#fff}.node-selector{position:fixed;right:52px;top:42%;z-index:5;display:flex;flex-direction:column;align-items:center;gap:14px;padding:8px 5px}.node-selector::before{content:"";position:absolute;top:0;bottom:0;left:50%;width:2px;background:#ececf3;z-index:-1}.node-selector button{width:22px;height:22px;padding:0;border:0;background:#fff;color:#d2d2df;font-size:16px;line-height:22px;cursor:pointer}.node-selector button.active{color:#9b8cf0}.node-selector button:hover{color:#7565dc;transform:scale(1.2)}.conversation{width:min(940px,100%);flex:1}.message-block{scroll-margin-top:24px}.user-message{display:flex;flex-direction:column;align-items:flex-end;margin:16px 0 44px}.user-message span,.user-message textarea{max-width:70%;width:auto;padding:12px 18px;border-radius:20px;background:#edf4ff;color:#273449;font-size:17px;line-height:1.6}.user-message textarea{min-width:280px;border:0;outline:0;resize:none}.message-actions,.edit-actions{display:flex;gap:8px;margin-top:10px}.message-actions button{border:0;background:transparent;color:#9aa1ac;font-size:19px;cursor:pointer}.edit-actions button{padding:5px 12px;border:1px solid #d7dce5;border-radius:8px;background:#fff;color:#586170;cursor:pointer}.assistant-message{max-width:760px;margin:0 auto 52px}.thinking-toggle{display:flex;align-items:center;gap:9px;border:0;background:transparent;color:#606b7b;font-size:17px;cursor:pointer;padding:0}.thinking-icon{position:relative;display:inline-block;width:20px;height:20px;color:#c7b8f4}.thinking-icon .pad{position:absolute;display:block;background:currentColor;border-radius:50%}.thinking-icon .pad-main{width:10px;height:9px;left:5px;top:9px}.thinking-icon .pad-left{width:6px;height:8px;left:1px;top:6px;transform:rotate(-28deg)}.thinking-icon .pad-right{width:6px;height:8px;right:1px;top:6px;transform:rotate(28deg)}.thinking-icon .pad-top{width:6px;height:8px;left:7px;top:1px}.thinking-toggle .el-icon{transition:transform .2s}.thinking-toggle .rotated{transform:rotate(180deg)}.thinking-content{margin:14px 0;padding-left:18px;border-left:2px solid #e5e8ef;color:#8a93a1;font-size:15px;line-height:1.8}.answer-content{margin-top:14px;color:#303846;font-size:17px;line-height:1.85}.answer-content:deep(p){margin:10px 0}.answer-actions{display:flex;gap:14px;margin-top:18px}.answer-actions button{border:0;background:transparent;color:#9aa1ac;font-size:19px;cursor:pointer}.composer{width:min(960px,100%);border:1px solid #e3e7ed;border-radius:20px;padding:16px;box-shadow:0 4px 18px rgba(35,48,70,.08);background:#fff}.uploaded-file{display:flex;align-items:center;gap:12px;width:max-content;max-width:100%;padding:10px 16px;margin-bottom:12px;border:1px solid #e1e5ec;border-radius:18px}.file-icon{width:32px;height:34px;display:grid;place-items:center;color:#3f86f5;background:#e9f1ff;border-radius:6px;font-size:22px}.file-meta{display:flex;flex-direction:column;gap:2px;min-width:0}.file-meta strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:16px;font-weight:500}.file-meta small{color:#8a919d;font-size:14px}.uploaded-file button{border:0;background:transparent;color:#9aa1ac;font-size:20px;cursor:pointer}.file-input{display:none}.composer textarea{display:block;width:100%;border:0;resize:none;outline:0;font:inherit;font-size:17px;line-height:1.6}.composer-toolbar{display:flex;align-items:center;gap:10px}.model-dropdown{margin-left:auto}.model-picker{display:flex;align-items:center;gap:4px;border:0;background:transparent;color:#626b78;font-size:15px;cursor:pointer}.attach{border:0;background:transparent;font-size:22px;color:#626b78;cursor:pointer}.send{width:42px;height:42px;border:0;border-radius:50%;background:#b7adf0;color:#fff;font-size:20px;display:grid;place-items:center;cursor:pointer}.send:disabled{opacity:.45}.disclaimer{margin:10px 0 0;color:#9aa1ac;font-size:13px}@media(max-width:640px){.query-view{padding:20px 14px}.node-selector{right:28px}.user-message span,.user-message textarea{max-width:90%}.assistant-message{width:100%}.composer{border-radius:16px}}
</style>
<style>
.uploaded-file { width: min(300px, 100%); }
.uploaded-file.success { border-color: #b7e2c1; background: #f3fbf5; }
.uploaded-file.error { border-color: #f0b7b7; background: #fff5f5; }
.uploaded-file.success .file-icon { color: #28a745; background: #ddf5e3; }
.uploaded-file.error .file-icon { color: #dc3545; background: #ffe0e0; }
.uploaded-file.success .file-meta small { color: #269344; }
.uploaded-file.error .file-meta small { color: #c63c3c; }
.progress-track { display: block; height: 4px; margin-top: 4px; overflow: hidden; border-radius: 4px; background: #e8ebf0; }
.progress-track i { display: block; height: 100%; border-radius: inherit; background: #7d9cf5; transition: width .2s; }
</style>
