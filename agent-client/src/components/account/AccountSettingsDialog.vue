<template>
  <el-dialog v-model="visible" class="settings-dialog" width="min(900px, calc(100vw - 32px))" :show-close="false" append-to-body destroy-on-close @open="loadProfile" @closed="cancelEditing">
    <template #header>
      <div class="dialog-header">
        <strong>系统设置</strong>
        <el-button text circle title="关闭" aria-label="关闭" @click="visible = false"><el-icon><Close /></el-icon></el-button>
      </div>
    </template>

    <div class="settings-layout">
      <nav class="settings-nav" aria-label="设置分类">
        <button class="active" type="button"><el-icon><User /></el-icon><span>账号管理</span></button>
      </nav>

      <main class="settings-content">
        <div v-if="loading && !user" class="loading"><el-icon class="is-loading"><Loading /></el-icon><span>正在加载账号信息</span></div>
        <el-alert v-else-if="loadError" title="账号信息加载失败" type="error" show-icon :closable="false">
          <template #default><el-button link type="primary" @click="loadProfile">重新加载</el-button></template>
        </el-alert>
        <template v-else-if="user">
          <div class="account-summary">
            <el-avatar :size="54">{{ initial }}</el-avatar>
            <div><strong>{{ user.username }}</strong><span>当前登录账号</span></div>
            <div class="summary-actions">
              <el-button v-if="!editing" :icon="Edit" @click="startEditing">编辑资料</el-button>
              <el-button v-if="!editing" :icon="Refresh" :loading="loading" text title="刷新资料" aria-label="刷新资料" @click="loadProfile" />
            </div>
          </div>
          <el-form v-if="editing" ref="formRef" class="profile-form" :model="form" :rules="rules" label-position="left" label-width="110px">
            <el-form-item label="用户名" prop="username"><el-input v-model="form.username" maxlength="20" show-word-limit /></el-form-item>
            <el-form-item label="用户 ID"><el-input :model-value="String(user.user_id)" disabled /></el-form-item>
            <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" maxlength="255" clearable placeholder="请输入邮箱" /></el-form-item>
            <el-form-item label="手机号码" prop="phone"><el-input v-model="form.phone" maxlength="11" clearable placeholder="请输入手机号" /></el-form-item>
            <div class="form-actions"><el-button @click="cancelEditing">取消</el-button><el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button></div>
          </el-form>
          <dl v-else class="info-list">
            <div><dt>用户名</dt><dd>{{ user.username }}</dd></div>
            <div><dt>用户 ID</dt><dd>{{ user.user_id }}</dd></div>
            <div><dt>邮箱</dt><dd :class="{ empty: !user.email }">{{ user.email || '未设置' }}</dd></div>
            <div><dt>手机号码</dt><dd :class="{ empty: !user.phone }">{{ user.phone || '未设置' }}</dd></div>
          </dl>
          <div class="logout-row">
            <div><strong>退出当前账号</strong><span>退出后需要重新登录才能访问工作台</span></div>
            <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
          </div>
        </template>
      </main>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { Close, Edit, Loading, Refresh, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'

const visible = defineModel<boolean>({ required: true })
const authStore = useAuthStore()
const { handleLogout } = useAuth()
const loading = ref(false)
const loadError = ref(false)
const editing = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ username: '', email: '', phone: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 6, max: 20, message: '用户名长度为 6-20 个字符', trigger: 'blur' }],
  email: [{ validator: (_rule, value, callback) => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? callback() : callback(new Error('请输入有效的邮箱地址')), trigger: 'blur' }],
  phone: [{ validator: (_rule, value, callback) => !value || /^\d{6,11}$/.test(value) ? callback() : callback(new Error('手机号应为 6-11 位数字')), trigger: 'blur' }],
}
const user = computed(() => authStore.user)
const initial = computed(() => user.value?.username.charAt(0).toUpperCase() || 'U')

async function loadProfile() {
  loading.value = true
  loadError.value = false
  try { await authStore.refreshUser() } catch { loadError.value = true } finally { loading.value = false }
}
function fillForm() {
  if (!user.value) return
  form.username = user.value.username
  form.email = user.value.email || ''
  form.phone = user.value.phone || ''
}
function startEditing() { fillForm(); editing.value = true }
function cancelEditing() { editing.value = false; formRef.value?.clearValidate() }
async function saveProfile() {
  if (!formRef.value || !await formRef.value.validate().catch(() => false)) return
  saving.value = true
  try {
    await authStore.updateUser({ username: form.username.trim(), email: form.email.trim() || null, phone: form.phone.trim() || null })
    editing.value = false
    ElMessage.success('个人信息已更新')
  } finally { saving.value = false }
}
</script>

<style lang="scss">
.settings-dialog { margin-top: max(5vh, 24px); border-radius: 8px; overflow: hidden; }
.settings-dialog .el-dialog__header { padding: 0; margin: 0; }
.settings-dialog .el-dialog__body { padding: 0; }
.dialog-header { height: 68px; padding: 0 22px 0 26px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #ececef; }
.dialog-header strong { font-size: 17px; }
.settings-layout { min-height: 500px; display: grid; grid-template-columns: 220px minmax(0, 1fr); }
.settings-nav { padding: 24px 14px; border-right: 1px solid #ececef; background: #fafafa; }
.settings-nav button { width: 100%; height: 48px; padding: 0 14px; display: flex; align-items: center; gap: 11px; border: 1px solid transparent; border-radius: 7px; color: var(--ink-900); background: transparent; font-size: 15px; cursor: default; }
.settings-nav button.active { border-color: var(--brand-500); background: #e9ebee; box-shadow: 0 0 0 2px var(--brand-100); }
.settings-content { min-width: 0; padding: 24px 34px 40px; }
.loading { min-height: 300px; display: grid; place-content: center; justify-items: center; gap: 12px; color: var(--ink-600); font-size: 14px; }
.account-summary { min-height: 82px; display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #e5e5e7; }
.account-summary :deep(.el-avatar) { flex: 0 0 auto; color: var(--brand-700); background: var(--brand-100); font-size: 20px; font-weight: 700; }
.account-summary div { min-width: 0; flex: 1; }
.account-summary .summary-actions { flex: 0 0 auto; display: flex; align-items: center; }
.account-summary strong, .account-summary span { display: block; overflow-wrap: anywhere; }
.account-summary strong { margin-bottom: 4px; font-size: 16px; }
.account-summary span, .logout-row span { color: #8a8790; font-size: 12px; }
.info-list { margin: 0; }
.info-list > div { min-height: 76px; display: grid; grid-template-columns: 140px minmax(0, 1fr); align-items: center; border-bottom: 1px solid #e5e5e7; }
.info-list dt { color: var(--ink-900); font-size: 14px; }
.info-list dd { margin: 0; overflow-wrap: anywhere; text-align: right; font-size: 14px; }
.info-list dd.empty { color: #9b98a0; }
.profile-form { padding: 20px 0 4px; border-bottom: 1px solid #e5e5e7; }
.profile-form :deep(.el-form-item) { min-height: 52px; margin-bottom: 12px; align-items: center; }
.profile-form :deep(.el-form-item__label) { color: var(--ink-900); }
.form-actions { padding: 4px 0 16px; display: flex; justify-content: flex-end; gap: 8px; }
.logout-row { min-height: 92px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 1px solid #e5e5e7; }
.logout-row strong, .logout-row span { display: block; }
.logout-row strong { margin-bottom: 6px; font-size: 14px; }
@media (max-width: 680px) {
  .settings-dialog { margin-top: 16px; }
  .settings-layout { min-height: 520px; grid-template-columns: 1fr; }
  .settings-nav { padding: 10px 14px; border-right: 0; border-bottom: 1px solid #ececef; }
  .settings-nav button { height: 42px; }
  .settings-content { padding: 16px 20px 32px; }
  .account-summary { flex-wrap: wrap; padding: 14px 0; }
  .account-summary .summary-actions { width: 100%; justify-content: flex-end; }
  .info-list > div { grid-template-columns: 100px minmax(0, 1fr); }
  .logout-row { align-items: flex-start; flex-direction: column; padding: 22px 0; }
}
</style>
