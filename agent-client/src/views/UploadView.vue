<template>
  <div class="upload-view">
    <el-row :gutter="20">
      <!-- 左侧：上传区域 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h2>文档上传</h2>
              <p>上传工程技术文档，系统将自动解析和索引</p>
            </div>
          </template>

          <!-- 上传区域 -->
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            accept=".pdf,.docx,.doc,.txt"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、DOCX、TXT 格式，文件大小不超过10MB
              </div>
            </template>
          </el-upload>

          <!-- 上传进度 -->
          <el-alert
            v-if="uploadStatus"
            :title="uploadStatus"
            :type="uploadStatus === 'completed' ? 'success' : 'info'"
            show-icon
            :closable="false"
            style="margin-top: 20px"
          />
        </el-card>
      </el-col>

      <!-- 右侧：已上传文件列表 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h2>已上传文件</h2>
              <p>管理您上传的文档</p>
            </div>
          </template>

          <el-table :data="uploadedFiles" style="width: 100%" v-loading="loadingFiles">
            <el-table-column prop="filename" label="文件名" width="180">
              <template #default="{ row }">
                <el-link @click="downloadFile(row.filename)">{{ row.filename }}</el-link>
              </template>
            </el-table-column>
            
            <el-table-column prop="size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="created_at" label="上传时间" width="160">
              <template #default="{ row }">
                {{ formatDateTime(new Date(row.created_at * 1000)) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="downloadFile(row.filename)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty 
            v-if="!loadingFiles && uploadedFiles.length === 0" 
            description="暂无上传的文件"
            :image-size="80"
            style="margin-top: 20px"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadDocument, getFileList, downloadFile as downloadFileApi } from '@/api/upload'
import { useTaskPolling } from '@/composables/useTaskPolling'
import { formatFileSize, formatDateTime } from '@/utils/format'

const uploadStatus = ref('')
const selectedFile = ref<File | null>(null)
const loadingFiles = ref(false)
const uploadedFiles = ref<any[]>([])

const beforeUpload = (file: File) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
  }
  return isLt10M
}

const handleFileChange = async (file: any) => {
  selectedFile.value = file.raw
  
  if (!selectedFile.value) return

  try {
    uploadStatus.value = '正在上传...'
    const result = await uploadDocument(selectedFile.value)
    
    uploadStatus.value = `上传成功，任务ID: ${result.task_id}`
    
    // 开始轮询任务状态
    const { startPolling } = useTaskPolling()
    startPolling(
      async () => {
        const status = await fetchTaskStatus(result.task_id)
        return status
      },
      () => {
        uploadStatus.value = '文档处理完成！'
        ElMessage.success('文档上传并索引成功！')
        loadUploadedFiles() // 刷新文件列表
      }
    )
  } catch (error: any) {
    uploadStatus.value = '上传失败'
    ElMessage.error(error.message || '上传失败')
  }
}

async function fetchTaskStatus(taskId: string) {
  const { getTaskStatus } = await import('@/api/upload')
  const result = await getTaskStatus(taskId)
  return { status: result.status, error: result.error }
}

const loadUploadedFiles = async () => {
  loadingFiles.value = true
  try {
    const response = await getFileList()
    uploadedFiles.value = response.files || []
  } catch (error: any) {
    ElMessage.error(error.message || '获取文件列表失败')
  } finally {
    loadingFiles.value = false
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
    ElMessage.error(error.message || '下载失败')
  }
}

onMounted(() => {
  loadUploadedFiles()
})
</script>

<style scoped lang="scss">
.upload-view {
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

.el-upload {
  width: 100%;

  &__text {
    em {
      color: #409eff;
      font-style: normal;
    }
  }

  &__tip {
    text-align: center;
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
}
</style>
