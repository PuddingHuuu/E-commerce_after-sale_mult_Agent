<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Headset, Lock, ShoppingBag, User } from '@element-plus/icons-vue'
import type { Component } from 'vue'
import type { Role } from '@/types/api'
import { roleMeta } from '@/utils/labels'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const roles: { key: Role; icon: Component }[] = [
  { key: 'consumer', icon: User },
  { key: 'platform', icon: Headset },
  { key: 'merchant', icon: ShoppingBag },
]

const activeRole = computed<Role | null>(() => {
  const fromMeta = route.meta.role
  if (fromMeta === 'consumer' || fromMeta === 'platform' || fromMeta === 'merchant') {
    return fromMeta
  }
  const match = route.path.match(/^\/auth\/(consumer|platform|merchant)/)
  return match ? (match[1] as Role) : null
})

function goRole(role: Role): void {
  if (auth.isLoggedIn(role)) {
    router.push(roleMeta[role].home)
  } else {
    router.push(`/auth/${role}`)
  }
}

function userFor(role: Role) {
  return auth.userFor(role)
}
</script>

<template>
  <aside class="role-rail" aria-label="端切换">
    <p class="role-rail__head">切换端</p>
    <button
      v-for="item in roles"
      :key="item.key"
      class="role-tab"
      :class="{ 'is-active': activeRole === item.key }"
      :style="{ '--role-accent': roleMeta[item.key].accent }"
      type="button"
      @click="goRole(item.key)"
    >
      <span class="role-tab__icon">
        <el-icon><component :is="item.icon" /></el-icon>
        <i v-if="userFor(item.key)" class="role-tab__online" />
      </span>
      <span class="role-tab__copy">
        <strong>{{ roleMeta[item.key].label }}</strong>
        <small>{{ userFor(item.key)?.display_name || '未登录' }}</small>
      </span>
      <el-icon v-if="!userFor(item.key)" class="role-tab__lock"><Lock /></el-icon>
    </button>
    <p class="role-rail__hint">三个端独立登录</p>
  </aside>
</template>

<style scoped>
.role-rail {
  position: fixed;
  z-index: 50;
  top: 50%;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  width: 100px;
  padding: 10px 7px;
  border: 1px solid rgba(228, 228, 235, 0.9);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 46px rgba(27, 29, 35, 0.12);
  backdrop-filter: blur(18px);
  transform: translateY(-50%);
}

.role-rail__head {
  padding: 3px 4px 5px;
  color: #b1b1b9;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-align: center;
}

.role-tab {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 9px 4px 8px;
  border: 1px solid transparent;
  border-radius: 12px;
  color: #9898a1;
  background: transparent;
  cursor: pointer;
  transition:
    color 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}

.role-tab:hover {
  color: var(--role-accent);
  background: #fafafa;
  transform: translateY(-1px);
}

.role-tab.is-active {
  color: var(--role-accent);
  border-color: color-mix(in srgb, var(--role-accent) 18%, #ffffff);
  background: color-mix(in srgb, var(--role-accent) 7%, #ffffff);
}

.role-tab__icon {
  position: relative;
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  color: var(--role-accent);
  background: color-mix(in srgb, var(--role-accent) 9%, #ffffff);
  font-size: 16px;
}

.role-tab.is-active .role-tab__icon {
  color: #fff;
  background: var(--role-accent);
  box-shadow: 0 7px 16px color-mix(in srgb, var(--role-accent) 25%, transparent);
}

.role-tab__online {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 7px;
  height: 7px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #11b479;
}

.role-tab__copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  max-width: 100%;
}

.role-tab__copy strong {
  font-size: 10px;
  font-weight: 650;
  line-height: 1.2;
}

.role-tab__copy small {
  max-width: 84px;
  overflow: hidden;
  color: #b0b0b8;
  font-size: 8px;
  font-weight: 400;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tab__lock {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #c4c4cc;
  font-size: 8px;
}

.role-rail__hint {
  padding: 2px 0 0;
  color: #c0c0c7;
  font-size: 8px;
  text-align: center;
}

@media (max-width: 860px) {
  .role-rail {
    top: auto;
    right: 12px;
    bottom: 10px;
    left: 12px;
    flex-direction: row;
    align-items: stretch;
    width: auto;
    padding: 6px;
    border-radius: 16px;
    transform: none;
  }

  .role-rail__head,
  .role-rail__hint {
    display: none;
  }

  .role-tab {
    flex: 1;
    flex-direction: row;
    justify-content: center;
    gap: 6px;
    padding: 8px 6px;
  }

  .role-tab__icon {
    width: 27px;
    height: 27px;
    font-size: 14px;
  }

  .role-tab__copy {
    align-items: flex-start;
  }

  .role-tab__copy strong {
    font-size: 10px;
  }

  .role-tab__copy small,
  .role-tab__lock {
    display: none;
  }
}
</style>
