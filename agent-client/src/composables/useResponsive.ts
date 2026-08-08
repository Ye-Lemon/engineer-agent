import { computed } from 'vue'
import { useBreakpoints } from '@vueuse/core'

/**
 * 响应式断点的组合式函数
 */
export function useResponsive() {
  const breakpoints = useBreakpoints({
    xs: 576,
    sm: 768,
    md: 992,
    lg: 1200,
    xl: 1400,
  })

  // 判断是否为移动端
  const isMobile = computed(() => breakpoints.smaller('sm').value)

  // 判断是否为平板

  // 判断是否为桌面

  // 侧边栏是否应该折叠为图标模式
  const shouldCollapseSidebar = computed(() => {
    return breakpoints.between('sm', 'md').value
  })

  // 侧边栏是否应该完全隐藏（使用抽屉）
  const shouldHideSidebar = computed(() => {
    return breakpoints.smaller('sm').value
  })

  return {
    isMobile,
    shouldCollapseSidebar,
    shouldHideSidebar,
  }
}
