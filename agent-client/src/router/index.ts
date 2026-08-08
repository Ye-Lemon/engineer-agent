import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录', requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { title: '注册', requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'upload',
          name: 'Upload',
          component: () => import('@/views/UploadView.vue'),
          meta: { title: '文档上传' },
        },
        {
          path: 'files',
          name: 'Files',
          component: () => import('@/views/FilesView.vue'),
          meta: { title: '文件管理' },
        },
        {
          path: 'query',
          name: 'Query',
          component: () => import('@/views/QueryView.vue'),
          meta: { title: '智能问答' },
        },
        {
          path: 'report',
          name: 'Report',
          component: () => import('@/views/ReportView.vue'),
          meta: { title: '报告生成' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '页面不存在' },
    },
  ],
})

// 路由导航守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 工程AI智能体` : '工程AI智能体'

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页，重定向到首页
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
