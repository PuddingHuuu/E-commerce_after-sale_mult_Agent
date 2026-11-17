<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import {
  Box,
  ChatDotRound,
  Headset,
  Refresh,
  Tickets,
  Back,
} from '@element-plus/icons-vue'
import { useMockStore } from '@/stores/mock'
import { useAdminUiStore } from '@/stores/adminUi'
import { APP_NAME, DEMO_AGENT_NAME } from '@/config'
import OrderDetailDrawer from '@/components/admin/OrderDetailDrawer.vue'
import TicketDetailDrawer from '@/components/admin/TicketDetailDrawer.vue'
import CreateTicketDialog from '@/components/admin/CreateTicketDialog.vue'

const route = useRoute()
const mock = useMockStore()
const ui = useAdminUiStore()

const pageTitle = computed(() => String(route.meta.title ?? '工作台'))
const todayLabel = dayjs().format('M 月 D 日')

const waitingCount = computed(
  () => mock.db.conversations.filter((item) => item.status === 'waiting').length,
)

const pendingTicketCount = computed(
  () => mock.db.tickets.filter((item) => item.status === 'pending').length,
)

const navItems = computed(() => [
  {
    name: 'admin-workbench',
    label: '售后工作台',
    icon: ChatDotRound,
    badge: waitingCount.value,
  },
  {
    name: 'admin-orders',
    label: '订单查询',
    icon: Box,
    badge: 0,
  },
  {
    name: 'admin-tickets',
    label: '售后工单',
    icon: Tickets,
    badge: pendingTicketCount.value,
  },
])

function navigateToSection(navigate: () => void): void {
  ui.closeAll()
  navigate()
}

async function resetDemo(): Promise<void> {
  try {
    await ElMessageBox.confirm(
      '将清空当前浏览器中的演示会话、订单和工单，并恢复初始示例数据。',
      '重置演示数据',
      {
        confirmButtonText: '确认重置',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    mock.resetDemoData()
    ui.closeAll()
    ElMessage.success('演示数据已重置')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '重置失败')
    }
  }
}
</script>

<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <span class="sidebar-brand__mark">
          <el-icon><Headset /></el-icon>
        </span>
        <span class="sidebar-brand__copy">
          <strong>{{ APP_NAME }}</strong>
          <small>Agent Console</small>
        </span>
      </div>

      <div class="sidebar-section">
        <p class="sidebar-section__label">工作空间</p>
        <nav class="sidebar-nav">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            v-slot="{ navigate, isActive }"
            :to="{ name: item.name }"
            custom
          >
            <button
              class="nav-item"
              :class="{ 'is-active': isActive }"
              type="button"
              :title="item.label"
              @click="navigateToSection(navigate)"
            >
              <el-icon class="nav-item__icon">
                <component :is="item.icon" />
              </el-icon>
              <span class="nav-label">{{ item.label }}</span>
              <span v-if="item.badge > 0" class="nav-badge">{{ item.badge }}</span>
            </button>
          </router-link>
        </nav>
      </div>

      <div class="sidebar-section sidebar-section--tools">
        <p class="sidebar-section__label">演示工具</p>
        <router-link to="/service" class="side-tool" title="打开客户端页面">
          <el-icon><Back /></el-icon>
          <span class="nav-label">客户端预览</span>
        </router-link>
        <button class="side-tool" type="button" title="重置演示数据" @click="resetDemo">
          <el-icon><Refresh /></el-icon>
          <span class="nav-label">重置数据</span>
        </button>
      </div>

      <div class="sidebar-spacer" />

      <div class="agent-card">
        <span class="agent-avatar">橙</span>
        <span class="agent-copy">
          <strong>{{ DEMO_AGENT_NAME }}</strong>
          <small><i /> 在线服务中</small>
        </span>
      </div>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar">
        <div class="admin-topbar__left">
          <span class="console-badge">ADMIN CONSOLE</span>
          <span class="topbar-divider" />
          <strong>{{ pageTitle }}</strong>
          <span class="topbar-date">{{ todayLabel }}</span>
        </div>
        <div class="admin-topbar__right">
          <span class="demo-mode">
            <i />
            演示数据 · 双标签页实时同步
          </span>
          <span class="topbar-divider" />
          <span class="topbar-agent">
            <span class="topbar-agent__avatar">橙</span>
            <span>
              <strong>{{ DEMO_AGENT_NAME }}</strong>
              <small>在线</small>
            </span>
          </span>
        </div>
      </header>

      <section class="admin-content">
        <router-view />
      </section>
    </main>

    <OrderDetailDrawer />
    <TicketDetailDrawer />
    <CreateTicketDialog />
  </div>
</template>

<style scoped>
.admin-shell {
  --admin-brand: #e1251b;
  --admin-brand-deep: #b81b13;
  --chat-accent: #e33426;
  --chat-accent-deep: #c22116;
  --el-color-primary: #e1251b;
  --el-color-primary-light-3: #ea665f;
  --el-color-primary-light-5: #f0928d;
  --el-color-primary-light-7: #f6bfbb;
  --el-color-primary-light-8: #f9d3d1;
  --el-color-primary-light-9: #fce9e8;
  --el-color-primary-dark-2: #b41d15;
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at 92% 0%, rgba(225, 37, 27, 0.035), transparent 26%),
    #f4f5f7;
}

.admin-sidebar {
  display: flex;
  flex-direction: column;
  flex: 0 0 216px;
  width: 216px;
  padding: 20px 12px 14px;
  color: #d8d8dd;
  background:
    radial-gradient(circle at 18% -6%, rgba(255, 92, 68, 0.18), transparent 28%),
    linear-gradient(180deg, #1b1d22 0%, #17191e 100%);
  box-shadow: 8px 0 32px rgba(24, 25, 31, 0.08);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 9px 22px;
}

.sidebar-brand__mark {
  display: grid;
  place-items: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #ff7455, #d92217);
  box-shadow: 0 8px 20px rgba(225, 37, 27, 0.26);
  font-size: 18px;
}

.sidebar-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.sidebar-brand__copy strong {
  color: #f3f3f5;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.sidebar-brand__copy small {
  color: #6d6e77;
  font-size: 9px;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.sidebar-section {
  padding-bottom: 18px;
}

.sidebar-section--tools {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.055);
}

.sidebar-section__label {
  padding: 0 11px 8px;
  color: #62636d;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.12em;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 42px;
  padding: 0 11px;
  border-radius: 9px;
  color: #9c9da7;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.nav-item:hover {
  color: #e4e4e8;
  background: rgba(255, 255, 255, 0.045);
}

.nav-item.is-active {
  color: #fff;
  background: linear-gradient(90deg, rgba(225, 37, 27, 0.28), rgba(225, 37, 27, 0.09));
  box-shadow: inset 2px 0 0 #ff5d4d;
}

.nav-item__icon {
  flex: 0 0 auto;
  font-size: 16px;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-badge {
  display: grid;
  place-items: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  margin-left: auto;
  border-radius: 5px;
  color: #ffd9d4;
  background: rgba(225, 37, 27, 0.5);
  font-size: 9px;
  font-weight: 700;
}

.side-tool {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  height: 30px;
  padding: 0 11px;
  border-radius: 7px;
  color: #74757f;
  background: transparent;
  font-size: 10px;
  text-align: left;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.side-tool:hover {
  color: #c9c9cf;
  background: rgba(255, 255, 255, 0.04);
}

.sidebar-spacer {
  flex: 1;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 11px 10px;
  border: 1px solid rgba(255, 255, 255, 0.055);
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.035);
}

.agent-avatar {
  display: grid;
  place-items: center;
  flex: 0 0 30px;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #ff7154, #d42317);
  font-size: 11px;
  font-weight: 700;
}

.agent-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.agent-copy strong {
  color: #dedee2;
  font-size: 11px;
  font-weight: 600;
}

.agent-copy small {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #70717a;
  font-size: 9px;
}

.agent-copy i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #14b87a;
}

.admin-main {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  height: 100vh;
  overflow: hidden;
}

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 0 0 56px;
  min-height: 56px;
  padding: 0 24px;
  border-bottom: 1px solid rgba(228, 228, 235, 0.8);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(18px);
}

.admin-topbar__left,
.admin-topbar__right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.console-badge {
  padding: 3px 7px;
  border: 1px solid #ececf1;
  border-radius: 4px;
  color: #a1a1aa;
  background: #fafafb;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.09em;
}

.admin-topbar__left strong {
  color: #55555e;
  font-size: 12px;
  font-weight: 600;
}

.topbar-date {
  color: #b4b4bc;
  font-size: 10px;
}

.topbar-divider {
  width: 1px;
  height: 14px;
  background: #e8e8ed;
}

.demo-mode {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #9a9aa3;
  font-size: 9px;
}

.demo-mode i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #16b97d;
  box-shadow: 0 0 0 3px rgba(22, 185, 125, 0.09);
}

.topbar-agent {
  display: flex;
  align-items: center;
  gap: 7px;
}

.topbar-agent__avatar {
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

.topbar-agent > span:last-child {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.topbar-agent strong {
  color: #5e5e67;
  font-size: 10px;
  font-weight: 600;
}

.topbar-agent small {
  color: #0f9f6e;
  font-size: 8px;
}

.admin-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 20px 22px 22px;
  overflow: hidden;
}

@media (max-width: 1280px) {
  .admin-sidebar {
    flex-basis: 76px;
    width: 76px;
    padding: 18px 9px 12px;
  }

  .sidebar-brand {
    justify-content: center;
    padding: 2px 0 20px;
  }

  .sidebar-brand__copy,
  .sidebar-section__label,
  .sidebar-nav .nav-label,
  .sidebar-section--tools .nav-label,
  .agent-copy {
    display: none;
  }

  .nav-item {
    justify-content: center;
    gap: 0;
    height: 44px;
    padding: 0;
  }

  .nav-badge {
    position: absolute;
    top: 6px;
    right: 8px;
    min-width: 14px;
    height: 14px;
    padding: 0 3px;
    border-radius: 4px;
    font-size: 8px;
  }

  .side-tool {
    justify-content: center;
    padding: 0;
  }

  .agent-card {
    justify-content: center;
    padding: 8px 0;
  }

  .sidebar-section {
    padding-bottom: 12px;
  }

  .sidebar-section--tools {
    padding-top: 12px;
  }

  .admin-content {
    padding: 16px;
  }

  .admin-topbar {
    padding: 0 16px;
  }
}

@media (max-width: 900px) {
  .admin-topbar__left .topbar-date,
  .demo-mode {
    display: none;
  }

  .admin-content {
    padding: 12px;
  }
}
</style>
