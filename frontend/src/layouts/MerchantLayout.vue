<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, ShoppingBag } from '@element-plus/icons-vue'
import RoleRail from '@/components/layout/RoleRail.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const user = computed(() => auth.userFor('merchant'))

async function logout(): Promise<void> {
  await auth.logout('merchant')
  ElMessage.success('已退出商家端')
  router.replace('/auth/merchant')
}
</script>

<template>
  <div class="portal-shell merchant-shell">
    <header class="merchant-header">
      <div class="merchant-header__inner">
        <router-link to="/merchant/conversations" class="merchant-brand">
          <span class="merchant-brand__mark"><el-icon><ShoppingBag /></el-icon></span>
          <span class="merchant-brand__copy">
            <strong>橙心售后</strong>
            <small>MERCHANT CENTER</small>
          </span>
        </router-link>

        <div class="merchant-nav">
          <span><el-icon><ChatDotRound /></el-icon> 协同会话</span>
        </div>

        <div class="merchant-user">
          <span class="merchant-store">{{ user?.store_name || user?.display_name || '商家' }}</span>
          <span class="merchant-user__avatar">{{ user?.display_name?.slice(0, 1) || '商' }}</span>
          <button type="button" class="merchant-logout" @click="logout">退出</button>
        </div>

        <RoleRail class="merchant-role-switch" />
      </div>
    </header>

    <main class="merchant-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.merchant-shell {
  --chat-accent: #7d9b84;
  --chat-accent-deep: #67826e;
  background:
    radial-gradient(circle at 7% 0%, rgba(125, 155, 132, 0.08), transparent 26%),
    #f5f8f5;
}

.merchant-header {
  position: sticky;
  z-index: 20;
  top: 0;
  height: 68px;
  border-bottom: 1px solid #dce7df;
  background:
    radial-gradient(circle at 4% -30%, rgba(125, 155, 132, 0.12), transparent 30%),
    rgba(255, 255, 255, 0.94);
  box-shadow: 0 2px 14px rgba(92, 116, 99, 0.08);
  backdrop-filter: blur(16px);
}

.merchant-header__inner {
  display: flex;
  align-items: center;
  gap: 28px;
  width: min(1400px, calc(100% - 36px));
  height: 100%;
  margin: 0 auto;
}

.merchant-brand {
  display: flex;
  align-items: center;
  gap: 9px;
}

.merchant-brand__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #9db8a5, #7d9b84);
  box-shadow: 0 6px 16px rgba(125, 155, 132, 0.22);
  font-size: 16px;
}

.merchant-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.merchant-brand__copy strong {
  color: #263630;
  font-size: 14px;
  font-weight: 700;
}

.merchant-brand__copy small {
  color: #8b9c90;
  font-size: 11px;
  letter-spacing: 0.12em;
}

.merchant-nav {
  display: flex;
  align-items: center;
  gap: 5px;
}

.merchant-nav span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 13px;
  border-radius: 9px;
  color: #55705c;
  background: #eef5ef;
  font-size: 13px;
}

.merchant-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.merchant-store {
  max-width: 220px;
  overflow: hidden;
  color: #5c6f61;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-user__avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #9db8a5, #7d9b84);
  font-size: 12px;
  font-weight: 700;
}

.merchant-logout {
  margin-left: 4px;
  padding: 5px 6px;
  color: #8b9c90;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.merchant-logout:hover {
  color: #67826e;
}

.merchant-role-switch {
  margin-left: 2px;
}

.merchant-main {
  width: min(1400px, calc(100% - 36px));
  margin: 0 auto;
  padding: 22px 0 32px;
}

@media (max-width: 1150px) {
  .merchant-header__inner {
    gap: 16px;
  }
}

@media (max-width: 1000px) {
  .merchant-store {
    display: none;
  }
}

@media (max-width: 860px) {
  .merchant-header {
    height: 60px;
  }

  .merchant-header__inner {
    gap: 10px;
    width: calc(100% - 20px);
  }

  .merchant-brand__copy small,
  .merchant-store,
  .merchant-logout,
  .merchant-nav {
    display: none;
  }

  .merchant-brand__mark {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    font-size: 16px;
  }

  .merchant-brand__copy strong {
    font-size: 13px;
  }

  .merchant-main {
    width: calc(100% - 18px);
    padding: 12px 0 16px;
  }
}
</style>
