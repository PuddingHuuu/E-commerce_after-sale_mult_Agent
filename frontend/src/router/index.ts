import { createRouter, createWebHistory } from 'vue-router'
import { APP_NAME } from '@/config'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/service',
    },
    {
      path: '/service',
      name: 'customer-service',
      component: () => import('@/pages/customer/CustomerServicePage.vue'),
      meta: { title: '客户服务' },
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      redirect: '/admin/workbench',
      children: [
        {
          path: 'workbench',
          name: 'admin-workbench',
          component: () => import('@/pages/admin/WorkbenchPage.vue'),
          meta: { title: '售后工作台' },
        },
        {
          path: 'orders',
          name: 'admin-orders',
          component: () => import('@/pages/admin/OrdersPage.vue'),
          meta: { title: '订单查询' },
        },
        {
          path: 'tickets',
          name: 'admin-tickets',
          component: () => import('@/pages/admin/TicketsPage.vue'),
          meta: { title: '售后工单' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/service',
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${String(to.meta.title)} · ${APP_NAME}`
    : `${APP_NAME} · 售后工单 Agent`
})

export default router
