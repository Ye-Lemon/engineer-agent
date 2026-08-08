<template>
  <div class="query-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>智能问答</h2>
          <p>基于RAG技术的工程技术问题智能解答</p>
        </div>
      </template>

      <!-- 输入区域 -->
      <div class="input-section">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题，例如：C30混凝土的配合比是什么？"
          @keyup.ctrl.enter="handleSubmit"
        />
        <div class="input-actions">
          <el-select v-model="topK" placeholder="检索数量" style="width: 120px; margin-right: 12px">
            <el-option label="Top 3" :value="3" />
            <el-option label="Top 5" :value="5" />
            <el-option label="Top 10" :value="10" />
          </el-select>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ loading ? '思考中...' : '发送' }}
          </el-button>
        </div>
      </div>

      <!-- 回答结果 -->
      <div v-if="queryResult" class="result-section">
        <el-divider />
        
        <!-- AI回答 -->
        <div class="answer-box">
          <div class="answer-header">
            <el-icon :size="24" color="#409eff"><ChatDotRound /></el-icon>
            <span>AI助手回答</span>
            <el-tag size="small" type="info">{{ queryResult.processing_time_ms }}ms</el-tag>
          </div>
          <div class="answer-content" v-html="renderedAnswer"></div>
        </div>

        <!-- 引用来源 -->
        <div v-if="queryResult.sources.length > 0" class="sources-box">
          <h4>引用来源 ({{ queryResult.sources.length }})</h4>
          <el-collapse accordion>
            <el-collapse-item
              v-for="(source, index) in queryResult.sources"
              :key="index"
              :name="index"
            >
              <template #title>
                <div class="source-title">
                  <el-tag size="small" type="success">#{{ index + 1 }}</el-tag>
                  <span class="source-name">{{ source.source }}</span>
                  <span v-if="source.page" class="source-page">第{{ source.page }}页</span>
                  <span v-if="source.similarity" class="source-sim">
                    相似度: {{ (source.similarity * 100).toFixed(1) }}%
                  </span>
                </div>
              </template>
              <div class="source-content">{{ source.content }}</div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 空状态提示 -->
      <el-empty v-else description="输入您的问题，开始智能问答" :image-size="120" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { queryKnowledge } from '@/api/query'
import type { QueryResponse } from '@/types'
import { marked } from 'marked'

const question = ref('')
const topK = ref(5)
const loading = ref(false)
const queryResult = ref<QueryResponse | null>(null)

const renderedAnswer = computed(() => {
  if (!queryResult.value) return ''
  return marked(queryResult.value.answer)
})

const handleSubmit = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  loading.value = true
  try {
    const result = await queryKnowledge({
      question: question.value,
      top_k: topK.value,
    })
    
    queryResult.value = result
    ElMessage.success('查询成功')
  } catch (error: any) {
    ElMessage.error(error.message || '查询失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.query-view {
  max-width: 900px;
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

.input-section {
  .input-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 12px;
  }
}

.result-section {
  margin-top: 20px;
}

.answer-box {
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
  padding: 16px;
  border-radius: 4px;

  .answer-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-weight: bold;
    color: #303133;
  }

  .answer-content {
    line-height: 1.8;
    color: #606266;

    :deep(p) {
      margin: 8px 0;
    }

    :deep(code) {
      background-color: #eef1f6;
      padding: 2px 6px;
      border-radius: 3px;
    }

    :deep(pre) {
      background-color: #282c34;
      color: #abb2bf;
      padding: 12px;
      border-radius: 4px;
      overflow-x: auto;
    }
  }
}

.sources-box {
  margin-top: 20px;

  h4 {
    margin: 0 0 12px;
    font-size: 16px;
    color: #303133;
  }

  .source-title {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;

    .source-name {
      flex: 1;
      font-weight: 500;
    }

    .source-page,
    .source-sim {
      font-size: 12px;
      color: #909399;
    }
  }

  .source-content {
    padding: 8px;
    background-color: #fafafa;
    border-radius: 4px;
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
  }
}
</style>
