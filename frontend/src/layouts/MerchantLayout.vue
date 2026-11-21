<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, ShoppingBag } from '@element-plus/icons-vue'
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
      </div>
    </header>

    <main class="merchant-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.merchant-shell {
  --chat-accent: #128c89;
  --chat-accent-deep: #0b6f6d;
  background:
    radial-gradient(circle at 7% 0%, rgba(22, 160, 155, 0.08), transparent 26%),
    #f4f7f7;
}

.merchant-header {
  position: sticky;
  z-index: 20;
  top: 0;
  height: 62px;
  border-bottom: 1px solid rgba(220, 234, 234, 0.9);
  background:
    radial-gradient(circle at 4% -30%, rgba(29, 180, 172, 0.16), transparent 30%),
    #0f2d30;
}

.merchant-header__inner {
  display: flex;
  align-items: center;
  gap: 28px;
  width: min(1240px, calc(100% - 44px));
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
  width: 33px;
  height: 33px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(145deg, #3ac6bd, #0f8584);
  font-size: 16px;
}

.merchant-brand__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.merchant-brand__copy strong {
  color: #f0fafa;
  font-size: 13px;
  font-weight: 700;
}

.merchant-brand__copy small {
  color: #5f8d8f;
  font-size: 7px;
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
  gap: 5px;
  height: 30px;
  padding: 0 10px;
  border-radius: 7px;
  color: #d3f0ee;
  background: rgba(45, 179, 171, 0.18);
  font-size: 10px;
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
  color: #b9d9d7;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-user__avatar {
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(145deg, #3bc9c1, #117f7e);
  font-size: 10px;
  font-weight: 700;
}

.merchant-logout {
  margin-left: 3px;
  padding: 4px 4px;
  color: #5f8a8c;
  background: transparent;
  font-size: 8px;
  cursor: pointer;
}

.merchant-logout:hover {
  color: #7ee1db;
}

.merchant-main {
  width: min(1240px, calc(100% - 44px));
  margin: 0 auto;
  padding: 20px 0 30px;
}

@media (max-width: 860px) {
  .merchant-header {
    height: 54px;
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
    width: 29px;
    height: 29px;
    font-size: 14px;
  }

  .merchant-brand__copy strong {
    font-size: 11px;
  }

  .merchant-main {
    width: calc(100% - 18px);
    padding: 12px 0 16px;
  }
}
</style>
