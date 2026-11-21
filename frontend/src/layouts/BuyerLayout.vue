<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight, Box, Headset, User } from '@element-plus/icons-vue'
import RoleRail from '@/components/layout/RoleRail.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const user = computed(() => auth.userFor('consumer'))
const navItems = [
  { label: '我的订单', path: '/consumer/orders', icon: Box },
  { label: '售后服务', path: '/consumer/after-sales', icon: Headset },
  { label: '在线客服', path: '/consumer/chat', icon: User },
]

function isActive(path: string): boolean {
  return route.path.startsWith(path)
}

async function logout(): Promise<void> {
  await auth.logout('consumer')
  ElMessage.success('已退出消费者端')
  router.replace('/auth/consumer')
}
</script>

<template>
  <div class="portal-shell buyer-shell">
    <header class="buyer-header">
      <div class="buyer-header__inner">
        <router-link to="/consumer/orders" class="buyer-brand">
          <span class="buyer-brand__mark"><el-icon><Headset /></el-icon></span>
          <span class="buyer-brand__copy">
            <strong>橙心售后</strong>
            <small>消费者中心</small>
          </span>
        </router-link>

        <nav class="buyer-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="buyer-nav__item"
            :class="{ 'is-active': isActive(item.path) }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            {{ item.label }}
          </router-link>
        </nav>

        <div class="buyer-user">
          <span class="buyer-user__avatar">
            {{ user?.display_name?.slice(0, 1) || '客' }}
          </span>
          <span class="buyer-user__copy">
            <strong>{{ user?.display_name || '消费者' }}</strong>
            <small>消费者端</small>
          </span>
          <button type="button" class="buyer-logout" @click="logout">
            退出
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>

        <RoleRail class="buyer-role-switch" />
      </div>
    </header>

    <main class="buyer-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.buyer-shell {
  --chat-accent: #ff5c0a;
  --chat-accent-deep: #e94a00;
  background:
    radial-gradient(circle at 8% 0%, rgba(255, 127, 48, 0.08), transparent 25%),
    #f6f7f9;
}

.buyer-header {
  position: sticky;
  z-index: 20;
  top: 0;
  height: 68px;
  border-bottom: 1px solid rgba(233, 233, 238, 0.85);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px);
}

.buyer-header__inner {
  display: flex;
  align-items: center;
  gap: 28px;
  width: min(1400px, calc(100% - 36px));
  height: 100%;
  margin: 0 auto;
}

.buyer-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 0 0 auto;
}

.buyer-brand__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #ff8c2f, #ff5000);
  box-shadow: 0 7px 16px rgba(255, 80, 0, 0.2);
  font-size: 18px;
}

.buyer-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.buyer-brand__copy strong {
  color: #27272c;
  font-size: 14px;
  font-weight: 700;
}

.buyer-brand__copy small {
  color: #a5a5ad;
  font-size: 11px;
  letter-spacing: 0.04em;
}

.buyer-nav {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 100%;
}

.buyer-nav__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 13px;
  border-radius: 9px;
  color: #888892;
  font-size: 13px;
  font-weight: 500;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.buyer-nav__item:hover {
  color: #4e4e56;
  background: #f8f8fa;
}

.buyer-nav__item.is-active {
  color: #ed5100;
  background: #fff3ec;
  font-weight: 600;
}

.buyer-nav__item :deep(.el-icon) {
  font-size: 14px;
}

.buyer-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.buyer-user__avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #ffa05c, #ef5a13);
  font-size: 13px;
  font-weight: 700;
}

.buyer-user__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.2;
}

.buyer-user__copy strong {
  color: #4f4f57;
  font-size: 12px;
  font-weight: 600;
}

.buyer-user__copy small {
  color: #a9a9b1;
  font-size: 11px;
}

.buyer-logout {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: 4px;
  padding: 5px 0;
  color: #aaaab2;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.buyer-logout:hover {
  color: #ef5a13;
}

.buyer-role-switch {
  margin-left: 2px;
}

.buyer-main {
  width: min(1400px, calc(100% - 36px));
  margin: 0 auto;
  padding: 22px 0 32px;
}

@media (max-width: 1150px) {
  .buyer-header__inner {
    gap: 16px;
  }
}

@media (max-width: 1000px) {
  .buyer-nav__item :deep(.el-icon) {
    display: none;
  }

  .buyer-nav__item {
    padding: 0 8px;
  }
}

@media (max-width: 860px) {
  .buyer-header {
    height: 60px;
  }

  .buyer-header__inner {
    gap: 10px;
    width: calc(100% - 22px);
  }

  .buyer-brand__copy small,
  .buyer-user__copy,
  .buyer-logout {
    display: none;
  }

  .buyer-brand__mark {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .buyer-brand__copy strong {
    font-size: 13px;
  }

  .buyer-nav {
    gap: 1px;
    margin-left: auto;
  }

  .buyer-nav__item {
    padding: 0 7px;
    font-size: 12px;
  }

  .buyer-nav__item :deep(.el-icon) {
    display: none;
  }

  .buyer-user {
    margin-left: 4px;
  }

  .buyer-main {
    width: calc(100% - 20px);
    padding: 14px 0 18px;
  }
}
</style>
