<template>
  <div class="files-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>文件管理</h2>
          <p>查看、下载和删除已上传的文档</p>
        </div>
      </template>

      <!-- 文件列表 -->
      <el-table :data="fileList" style="width: 100%" v-loading="loading">
        <el-table-column prop="filename" label="文件名" width="200">
          <template #default="{ row }">
            <el-link @click="downloadFile(row.filename)">{{ row.filename }}</el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(new Date(row.created_at * 1000)) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="downloadFile(row.filename)"
            >
              下载
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row.filename)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && fileList.length === 0" 
        description="暂无上传的文件"
        :image-size="120"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFileList, deleteFile, downloadFile as downloadFileApi } from '@/api/upload'
import { formatFileSize, formatDateTime } from '@/utils/format'

const loading = ref(false)
const fileList = ref<any[]>([])

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await getFileList()
    fileList.value = response.files || []
  } catch (error: any) {
    ElMessage.error(error.message || '获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (filename: string) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteFile(filename)
    ElMessage.success('文件删除成功')
    loadFiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除文件失败')
    }
  }
}

const downloadFile = async (filename: string) => {
  try {
    const blob = await downloadFileApi(filename)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '下载文件失败')
  }
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped lang="scss">
.files-view {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  h2 {
    margin: 0 0 8px;
    font-size: 24px;
    color: #303133;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: #909399;
  }
}
</style>

<style scoped lang="scss">
.files-view { max-width: 1240px; padding: 32px 30px 56px; }
.files-view :deep(.el-card) { border-radius: 16px; overflow: hidden; }
.files-view :deep(.el-card__header) { padding: 24px 28px; background: linear-gradient(180deg,#fff,#fcfbff); }
.files-view :deep(.el-table th.el-table__cell) { background: #faf9fd; color: #686277; font-weight: 600; }
.files-view :deep(.el-table td.el-table__cell), .files-view :deep(.el-table th.el-table__cell) { padding: 15px 0; }
@media (max-width: 720px) { .files-view { padding: 20px 16px 36px; } }
</style>
