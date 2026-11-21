<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, ChatDotRound, Headset, Tickets } from '@element-plus/icons-vue'
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
      </div>
    </header>

    <main class="platform-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.platform-shell {
  --chat-accent: #e22f21;
  --chat-accent-deep: #c41f14;
  background:
    radial-gradient(circle at 94% 0%, rgba(225, 37, 27, 0.04), transparent 26%),
    #f4f5f7;
}

.platform-header {
  position: sticky;
  z-index: 20;
  top: 0;
  height: 58px;
  background:
    radial-gradient(circle at 5% -20%, rgba(255, 93, 74, 0.18), transparent 28%),
    #1b1d22;
  box-shadow: 0 4px 18px rgba(20, 21, 25, 0.14);
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
  width: 31px;
  height: 31px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #ff7455, #d62318);
  font-size: 16px;
}

.platform-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.platform-brand__copy strong {
  color: #f2f2f4;
  font-size: 13px;
  font-weight: 700;
}

.platform-brand__copy small {
  color: #696a73;
  font-size: 7px;
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
  gap: 5px;
  height: 30px;
  padding: 0 11px;
  border-radius: 7px;
  color: #93949e;
  font-size: 10px;
  font-weight: 500;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.platform-nav__item:hover {
  color: #e5e5e8;
  background: rgba(255, 255, 255, 0.05);
}

.platform-nav__item.is-active {
  color: #fff;
  background: rgba(225, 37, 27, 0.3);
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
  font-size: 8px;
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
  width: 27px;
  height: 27px;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(145deg, #ff7455, #d42317);
  font-size: 10px;
  font-weight: 700;
}

.platform-user__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.2;
}

.platform-user__copy strong {
  color: #d6d6da;
  font-size: 9px;
  font-weight: 600;
}

.platform-user__copy small {
  color: #6e6f78;
  font-size: 8px;
}

.platform-logout {
  margin-left: 5px;
  padding: 4px 5px;
  color: #72737c;
  background: transparent;
  font-size: 8px;
  cursor: pointer;
}

.platform-logout:hover {
  color: #ff8172;
}

.platform-main {
  width: min(1400px, calc(100% - 36px));
  margin: 0 auto;
  padding: 20px 0 30px;
}

@media (max-width: 860px) {
  .platform-header {
    height: 54px;
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
    width: 28px;
    height: 28px;
    border-radius: 8px;
    font-size: 14px;
  }

  .platform-brand__copy strong {
    font-size: 11px;
  }

  .platform-nav {
    margin-left: auto;
  }

  .platform-nav__item {
    height: 27px;
    padding: 0 7px;
    font-size: 9px;
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
