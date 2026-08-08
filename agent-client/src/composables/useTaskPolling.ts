import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

/**
 * 任务轮询的组合式函数
 */
export function useTaskPolling() {
  const isPolling = ref(false)
  let pollInterval: number | null = null

  /**
   * 开始轮询任务状态
   */
  function startPolling(
    fetchStatus: () => Promise<{ status: string; error?: string }>,
    onComplete: () => void,
    interval = 2000
  ) {
    isPolling.value = true

    const poll = async () => {
      try {
        const result = await fetchStatus()

        if (result.status === 'completed') {
          stopPolling()
          onComplete()
        } else if (result.status === 'failed') {
          stopPolling()
          ElMessage.error(result.error || '任务处理失败')
        }
      } catch (error: any) {
        console.error('Polling error:', error)
        stopPolling()
        ElMessage.error('查询任务状态失败')
      }
    }

    // 立即执行一次
    poll()

    // 设置定时轮询
    pollInterval = window.setInterval(poll, interval)
  }

  /**
   * 停止轮询
   */
  function stopPolling() {
    isPolling.value = false
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    stopPolling()
  })

  return {
    isPolling,
    startPolling,
    stopPolling,
  }
}
