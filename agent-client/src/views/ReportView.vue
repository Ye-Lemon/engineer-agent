<template>
  <div class="report-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>报告生成</h2>
          <p>基于AI技术自动生成工程报告</p>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：参数配置 -->
        <el-col :xs="24" :sm="24" :md="10" :lg="8">
          <el-form :model="form" label-width="100px">
            <el-form-item label="报告类型">
              <el-select v-model="form.reportType" placeholder="请选择报告类型" @change="handleTypeChange">
                <el-option label="混凝土配合比设计" value="concrete_mix" />
                <el-option label="结构设计报告" value="structural_design" />
                <el-option label="荷载计算书" value="load_calculation" />
                <el-option label="材料技术规范" value="material_spec" />
              </el-select>
            </el-form-item>

            <!-- 动态参数表单 -->
            <template v-if="form.reportType === 'concrete_mix'">
              <el-form-item label="强度等级">
                <el-input v-model="form.params.strength_grade" placeholder="例如：C30" />
              </el-form-item>
              <el-form-item label="坍落度">
                <el-input v-model="form.params.slump" placeholder="例如：160mm" />
              </el-form-item>
              <el-form-item label="使用环境">
                <el-input v-model="form.params.environment" placeholder="例如：室内干燥环境" />
              </el-form-item>
              <el-form-item label="骨料类型">
                <el-input v-model="form.params.aggregate_type" placeholder="例如：碎石" />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleGenerate"
                style="width: 100%"
              >
                {{ loading ? '生成中...' : '生成报告' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>

        <!-- 右侧：报告内容 -->
        <el-col :xs="24" :sm="24" :md="14" :lg="16">
          <div v-if="reportContent" class="report-content">
            <div class="report-header">
              <h3>{{ getReportTitle(form.reportType) }}</h3>
              <el-tag>{{ reportData?.generated_at ? formatDateTime(reportData.generated_at) : '' }}</el-tag>
            </div>
            
            <el-divider />
            
            <div class="report-body" v-html="renderedContent"></div>

            <el-divider />

            <!-- 引用规范 -->
            <div v-if="reportData && reportData.references && reportData.references.length > 0" class="references">
              <h4>引用规范</h4>
              <el-table :data="reportData?.references || []" size="small">
                <el-table-column prop="standard_name" label="规范名称" width="180" />
                <el-table-column prop="section" label="章节" width="100" />
                <el-table-column prop="content" label="内容" />
              </el-table>
            </div>

            <div class="report-actions">
              <el-button @click="copyContent">
                <el-icon><DocumentCopy /></el-icon>
                复制内容
              </el-button>
              <el-button type="success" @click="downloadReport">
                <el-icon><Download /></el-icon>
                下载报告
              </el-button>
              <el-button type="primary" @click="saveToFiles">
                <el-icon><FolderAdd /></el-icon>
                保存到文件
              </el-button>
            </div>
          </div>

          <el-empty v-else description="填写参数并生成报告" :image-size="120" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy, Download, FolderAdd } from '@element-plus/icons-vue'
import { generateReport } from '@/api/report'
import type { ReportResponse } from '@/types'
import { marked } from 'marked'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const reportContent = ref('')
const reportData = ref<ReportResponse | null>(null)

const form = reactive({
  reportType: '',
  params: {} as Record<string, any>,
})

const renderedContent = computed(() => {
  if (!reportContent.value) return ''
  return marked(reportContent.value)
})

const handleTypeChange = () => {
  // 重置参数
  form.params = {}
  reportContent.value = ''
  reportData.value = null
}

const handleGenerate = async () => {
  if (!form.reportType) {
    ElMessage.warning('请选择报告类型')
    return
  }

  // 验证必要参数
  const requiredParams = getRequiredParams(form.reportType)
  for (const param of requiredParams) {
    if (!form.params[param]) {
      ElMessage.warning(`请填写${param}`)
      return
    }
  }

  loading.value = true
  try {
    const result = await generateReport({
      report_type: form.reportType,
      parameters: form.params,
    })
    
    reportData.value = result
    reportContent.value = result.content
    ElMessage.success('报告生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '报告生成失败')
  } finally {
    loading.value = false
  }
}

const getRequiredParams = (type: string): string[] => {
  const paramsMap: Record<string, string[]> = {
    concrete_mix: ['strength_grade', 'slump', 'environment', 'aggregate_type'],
    structural_design: ['structure_type', 'load_grade', 'seismic_intensity'],
    load_calculation: ['building_use', 'floors', 'structure_form'],
    material_spec: ['material_type', 'usage_location'],
  }
  return paramsMap[type] || []
}

const getReportTitle = (type: string): string => {
  const titles: Record<string, string> = {
    concrete_mix: '混凝土配合比设计报告',
    structural_design: '结构设计报告',
    load_calculation: '荷载计算书',
    material_spec: '材料技术规范',
  }
  return titles[type] || '工程报告'
}

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(reportContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

const downloadReport = () => {
  const blob = new Blob([reportContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${getReportTitle(form.reportType)}_${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

const saveToFiles = async () => {
  // 这里可以实现将生成的报告保存为文件的功能
  // 由于后端没有提供保存报告的API，暂时使用下载功能
  downloadReport()
}
</script>

<style scoped lang="scss">
.report-view {
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

.report-content {
  padding: 20px;
  background-color: #fff;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.report-body {
  line-height: 1.8;
  color: #606266;

  :deep(h1), :deep(h2), :deep(h3) {
    margin-top: 24px;
    margin-bottom: 12px;
  }

  :deep(p) {
    margin: 12px 0;
  }

  :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;

    th, td {
      border: 1px solid #dcdfe6;
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background-color: #f5f7fa;
    }
  }
}

.references {
  h4 {
    margin: 16px 0 12px;
    font-size: 16px;
    color: #303133;
  }
}

.report-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>

<style scoped lang="scss">
.report-view { max-width: 1240px; padding: 32px 30px 56px; }
.report-view :deep(.el-card) { border-radius: 16px; overflow: hidden; }
.report-view :deep(.el-card__header) { padding: 24px 28px; background: linear-gradient(180deg,#fff,#fcfbff); }
.report-view :deep(.el-form-item) { margin-bottom: 20px; }
.report-view :deep(.el-button) { border-radius: 9px; }
.report-content { border: 1px solid #ece8f2; border-radius: 14px; box-shadow: 0 8px 24px rgba(52,40,83,.04); }
.report-actions { flex-wrap: wrap; }
@media (max-width: 720px) { .report-view { padding: 20px 16px 36px; } }
</style>
