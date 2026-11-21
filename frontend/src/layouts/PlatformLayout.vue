<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, ChatDotRound, Headset, Tickets } from '@element-plus/icons-vue'
import RoleRail from '@/components/layout/RoleRail.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const user = computed(() => auth.userFor('platform'))

const navItems = [
  { label: '工单中心', path: '/platform/tickets', icon: Tickets },
  { label: '订单查询', path: '/platform/orders', icon: Box },
  { label: '用户会话', path: '/platform/conversations', icon: ChatDotRound },
]

function isActive(path: string): boolean {
  return route.path.startsWith(path)
}

async function logout(): Promise<void> {
  await auth.logout('platform')
  ElMessage.success('已退出平台客服端')
  router.replace('/auth/platform')
}
</script>

<template>
  <div class="portal-shell platform-shell">
    <header class="platform-header">
      <div class="platform-header__inner">
        <router-link to="/platform/tickets" class="platform-brand">
          <span class="platform-brand__mark"><el-icon><Headset /></el-icon></span>
          <span class="platform-brand__copy">
            <strong>橙心售后</strong>
            <small>PLATFORM CONSOLE</small>
          </span>
        </router-link>

        <nav class="platform-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="platform-nav__item"
            :class="{ 'is-active': isActive(item.path) }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            {{ item.label }}
          </router-link>
        </nav>

        <div class="platform-user">
          <span class="platform-online"><i /> 在线</span>
          <span class="platform-user__avatar">{{ user?.display_name?.slice(0, 1) || '服' }}</span>
          <span class="platform-user__copy">
            <strong>{{ user?.display_name || '平台客服' }}</strong>
            <small>平台客服端</small>
          </span>
          <button type="button" class="platform-logout" @click="logout">退出</button>
        </div>

        <RoleRail class="platform-role-switch" />
      </div>
    </header>

    <main class="platform-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.platform-shell {
  --chat-accent: #2f6fe4;
  --chat-accent-deep: #1d5bd6;
  background:
    radial-gradient(circle at 94% 0%, rgba(47, 111, 228, 0.06), transparent 30%),
    #f2f6fc;
}

.platform-header {
  position: sticky;
  z-index: 20;
  top: 0;
  height: 68px;
  border-bottom: 1px solid #dbe6f5;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 2px 14px rgba(47, 111, 228, 0.08);
  backdrop-filter: blur(16px);
}

.platform-header__inner {
  display: flex;
  align-items: center;
  gap: 28px;
  width: min(1400px, calc(100% - 36px));
  height: 100%;
  margin: 0 auto;
}

.platform-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 0 0 auto;
}

.platform-brand__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #4c8dff, #2f6fe4);
  box-shadow: 0 6px 16px rgba(47, 111, 228, 0.22);
  font-size: 16px;
}

.platform-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.platform-brand__copy strong {
  color: #1f2d52;
  font-size: 14px;
  font-weight: 700;
}

.platform-brand__copy small {
  color: #8b9bbf;
  font-size: 11px;
  letter-spacing: 0.12em;
}

.platform-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.platform-nav__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 13px;
  border-radius: 9px;
  color: #6b7a99;
  font-size: 13px;
  font-weight: 500;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.platform-nav__item:hover {
  color: #2f6fe4;
  background: #eef4ff;
}

.platform-nav__item.is-active {
  color: #2f6fe4;
  background: #eef4ff;
  font-weight: 600;
}

.platform-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.platform-online {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 7px;
  border-radius: 5px;
  color: #81d6b2;
  background: rgba(15, 159, 110, 0.1);
  font-size: 11px;
}

.platform-online i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #15c486;
}

.platform-user__avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #6a9cf0, #2f6fe4);
  box-shadow: 0 4px 12px rgba(47, 111, 228, 0.2);
  font-size: 12px;
  font-weight: 700;
}

.platform-user__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.2;
}

.platform-user__copy strong {
  color: #1f2d52;
  font-size: 12px;
  font-weight: 600;
}

.platform-user__copy small {
  color: #8b9bbf;
  font-size: 11px;
}

.platform-logout {
  margin-left: 4px;
  padding: 5px 6px;
  color: #8b9bbf;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.platform-logout:hover {
  color: #2f6fe4;
}

.platform-role-switch {
  margin-left: 2px;
}

.platform-main {
  width: min(1400px, calc(100% - 36px));
  margin: 0 auto;
  padding: 22px 0 32px;
}

@media (max-width: 1150px) {
  .platform-header__inner {
    gap: 16px;
  }
}

@media (max-width: 1000px) {
  .platform-online,
  .platform-user__copy {
    display: none;
  }

  .platform-nav__item :deep(.el-icon) {
    display: none;
  }
}

@media (max-width: 860px) {
  .platform-header {
    height: 60px;
  }

  .platform-header__inner {
    gap: 10px;
    width: calc(100% - 18px);
  }

  .platform-brand__copy small,
  .platform-online,
  .platform-user__copy,
  .platform-logout {
    display: none;
  }

  .platform-brand__mark {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    font-size: 16px;
  }

  .platform-brand__copy strong {
    font-size: 13px;
  }

  .platform-nav {
    margin-left: auto;
  }

  .platform-nav__item {
    height: 32px;
    padding: 0 9px;
    font-size: 12px;
  }

  .platform-nav__item :deep(.el-icon) {
    display: none;
  }

  .platform-user {
    margin-left: 2px;
  }

  .platform-main {
    width: calc(100% - 18px);
    padding: 12px 0 16px;
  }
}
</style>
