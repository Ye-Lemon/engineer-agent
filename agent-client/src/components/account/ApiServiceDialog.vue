<template>
  <el-dialog v-model="visible" class="api-dialog" width="min(620px, calc(100vw - 32px))" title="API 服务" append-to-body>
    <div class="api-intro">
      <span class="api-icon"><el-icon><Connection /></el-icon></span>
      <div><strong>工程 AI API</strong><p>通过标准 HTTP 接口接入当前服务。</p></div>
    </div>

    <dl class="api-details">
      <div>
        <dt>接口基础地址</dt>
        <dd><code>{{ apiBaseUrl }}</code><el-button text circle title="复制接口地址" aria-label="复制接口地址" @click="copyText(apiBaseUrl)"><el-icon><CopyDocument /></el-icon></el-button></dd>
      </div>
      <div>
        <dt>认证方式</dt>
        <dd><code>Authorization: Bearer &lt;token&gt;</code><el-button text circle title="复制认证格式" aria-label="复制认证格式" @click="copyText('Authorization: Bearer <token>')"><el-icon><CopyDocument /></el-icon></el-button></dd>
      </div>
      <div>
        <dt>接口文档</dt>
        <dd><code>{{ docsUrl }}</code><el-button text circle title="打开接口文档" aria-label="打开接口文档" @click="openDocs"><el-icon><TopRight /></el-icon></el-button></dd>
      </div>
    </dl>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" :icon="TopRight" @click="openDocs">打开接口文档</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Connection, CopyDocument, TopRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const visible = defineModel<boolean>({ required: true })
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api/v1`
const docsUrl = computed(() => {
  try {
    const url = new URL(apiBaseUrl, window.location.origin)
    url.pathname = url.pathname.replace(/\/api\/v1\/?$/, '/docs')
    return url.toString().replace(/\/$/, '')
  } catch { return `${window.location.origin}/docs` }
})

async function copyText(text: string) {
  try { await navigator.clipboard.writeText(text); ElMessage.success('已复制') } catch { ElMessage.error('复制失败') }
}
function openDocs() { window.open(docsUrl.value, '_blank', 'noopener,noreferrer') }
</script>

<style lang="scss">
.api-dialog { border-radius: 8px; }
.api-intro { padding: 2px 0 22px; display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #e5e5e7; }
.api-icon { width: 44px; height: 44px; flex: 0 0 44px; display: grid; place-items: center; border-radius: 7px; color: var(--brand-700); background: var(--brand-100); font-size: 20px; }
.api-intro strong { font-size: 16px; }
.api-intro p { margin: 5px 0 0; color: var(--ink-600); font-size: 13px; }
.api-details { margin: 0; }
.api-details > div { min-height: 78px; display: grid; grid-template-columns: 116px minmax(0, 1fr); align-items: center; gap: 16px; border-bottom: 1px solid #e5e5e7; }
.api-details dt { font-size: 14px; }
.api-details dd { min-width: 0; margin: 0; display: flex; align-items: center; justify-content: flex-end; gap: 5px; }
.api-details code { min-width: 0; overflow: hidden; color: var(--ink-600); font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 560px) {
  .api-details > div { padding: 15px 0; grid-template-columns: 1fr; gap: 7px; }
  .api-details dd { justify-content: space-between; }
}
</style>
