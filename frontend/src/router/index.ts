import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized, RouteRecordRaw } from 'vue-router'
import { APP_NAME } from '@/config'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/types/api'
import { roleMeta } from '@/utils/labels'

const authPage = () => import('@/pages/auth/AuthPage.vue')
const buyerLayout = () => import('@/layouts/BuyerLayout.vue')
const platformLayout = () => import('@/layouts/PlatformLayout.vue')
const merchantLayout = () => import('@/layouts/MerchantLayout.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: () => {
      const auth = useAuthStore()
      const available = auth.loggedRoles
      if (available.length) return roleMeta[available[0]].home
      return '/auth/consumer'
    },
  },
  {
    path: '/auth/:role(consumer|platform|merchant)',
    name: 'auth',
    component: authPage,
    meta: { title: '登录' },
  },
  {
    path: '/consumer',
    component: buyerLayout,
    meta: { role: 'consumer' },
    redirect: '/consumer/orders',
    children: [
      {
        path: 'orders',
        name: 'buyer-orders',
        component: () => import('@/pages/buyer/BuyerOrdersPage.vue'),
        meta: { title: '我的订单' },
      },
      {
        path: 'after-sales',
        name: 'buyer-after-sales',
        component: () => import('@/pages/buyer/BuyerTicketsPage.vue'),
        meta: { title: '售后服务' },
      },
      {
        path: 'after-sales/:id',
        name: 'buyer-ticket-detail',
        component: () => import('@/pages/buyer/BuyerTicketDetailPage.vue'),
        meta: { title: '售后详情' },
      },
      {
        path: 'chat',
        name: 'buyer-chat',
        component: () => import('@/pages/buyer/BuyerConversationsPage.vue'),
        meta: { title: '在线客服' },
      },
    ],
  },
  {
    path: '/platform',
    component: platformLayout,
    meta: { role: 'platform' },
    redirect: '/platform/tickets',
    children: [
      {
        path: 'tickets',
        name: 'platform-tickets',
        component: () => import('@/pages/platform/PlatformTicketsPage.vue'),
        meta: { title: '工单中心' },
      },
      {
        path: 'orders',
        name: 'platform-orders',
        component: () => import('@/pages/platform/PlatformOrdersPage.vue'),
        meta: { title: '订单查询' },
      },
      {
        path: 'conversations',
        name: 'platform-conversations',
        component: () => import('@/pages/platform/PlatformConversationsPage.vue'),
        meta: { title: '用户会话' },
      },
    ],
  },
  {
    path: '/merchant',
    component: merchantLayout,
    meta: { role: 'merchant' },
    redirect: '/merchant/conversations',
    children: [
      {
        path: 'conversations',
        name: 'merchant-conversations',
        component: () => import('@/pages/merchant/MerchantConversationsPage.vue'),
        meta: { title: '协同会话' },
      },
    ],
  },
  {
    path: '/service',
    redirect: '/consumer/orders',
  },
  {
    path: '/admin',
    redirect: '/platform/tickets',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

function requiredRole(to: RouteLocationNormalized): Role | null {
  const role = to.meta.role
  if (role === 'consumer' || role === 'platform' || role === 'merchant') return role

  return null
}

router.beforeEach((to) => {
  const role = requiredRole(to)
  if (!role) return true

  const auth = useAuthStore()
  if (!auth.isLoggedIn(role)) {
    return {
      name: 'auth',
      params: { role },
      query: { redirect: to.fullPath },
    }
  }
  return true
})

router.afterEach((to) => {
  const title = to.meta.title ? `${String(to.meta.title)} · ${APP_NAME}` : `${APP_NAME} · 多 Agent 售后协同`
  document.title = title
})

export default router
