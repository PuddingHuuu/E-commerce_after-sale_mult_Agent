<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Headset, Lock, ShoppingBag, User } from '@element-plus/icons-vue'
import type { Component } from 'vue'
import type { Role } from '@/types/api'
import { roleMeta } from '@/utils/labels'
import { useAuthStore } from '@/stores/auth'

const props = withDefaults(
  defineProps<{
    variant?: 'inline' | 'floating'
  }>(),
  {
    variant: 'inline',
  },
)

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

const variantClass = computed(() => `role-switch--${props.variant}`)
</script>

<template>
  <div
    class="role-switch"
    :class="variantClass"
    role="group"
    aria-label="切换端"
  >
    <button
      v-for="item in roles"
      :key="item.key"
      class="role-switch__tab"
      :class="{ 'is-active': activeRole === item.key }"
      :style="{ '--role-accent': roleMeta[item.key].accent }"
      type="button"
      :aria-label="`切换到${roleMeta[item.key].label}`"
      :title="roleMeta[item.key].label"
      @click="goRole(item.key)"
    >
      <span class="role-switch__icon">
        <el-icon><component :is="item.icon" /></el-icon>
        <i v-if="userFor(item.key)" class="role-switch__online" aria-hidden="true" />
        <el-icon v-else class="role-switch__lock" aria-hidden="true"><Lock /></el-icon>
      </span>
      <span class="role-switch__label">{{ roleMeta[item.key].label }}</span>
    </button>
  </div>
</template>

<style scoped>
.role-switch {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  flex: 0 0 auto;
  padding: 3px;
  border: 1px solid rgba(31, 45, 82, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 6px 20px rgba(31, 45, 82, 0.1);
  backdrop-filter: blur(12px);
}

.role-switch__tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 11px 0 7px;
  border: 1px solid transparent;
  border-radius: 999px;
  color: #6c7488;
  background: transparent;
  font-size: 13px;
  font-weight: 550;
  white-space: nowrap;
  cursor: pointer;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease;
}

.role-switch__tab:hover {
  color: var(--role-accent);
  background: color-mix(in srgb, var(--role-accent) 7%, #fff);
}

.role-switch__tab.is-active {
  color: var(--role-accent);
  border-color: color-mix(in srgb, var(--role-accent) 18%, #fff);
  background: color-mix(in srgb, var(--role-accent) 10%, #fff);
}

.role-switch__icon {
  position: relative;
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: var(--role-accent);
  background: color-mix(in srgb, var(--role-accent) 10%, #fff);
  font-size: 14px;
}

.role-switch__tab.is-active .role-switch__icon {
  color: #fff;
  background: var(--role-accent);
  box-shadow: 0 4px 10px color-mix(in srgb, var(--role-accent) 28%, transparent);
}

.role-switch__online {
  position: absolute;
  top: -1px;
  right: -1px;
  width: 7px;
  height: 7px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #11b479;
}

.role-switch__lock {
  position: absolute;
  top: -2px;
  right: -3px;
  padding: 1px;
  border-radius: 50%;
  color: #9aa3b5;
  background: #fff;
  font-size: 11px;
}

.role-switch__label {
  line-height: 1;
}

@media (min-width: 861px) {
  .role-switch--floating {
    display: none;
  }
}

@media (min-width: 861px) and (max-width: 1150px) {
  .role-switch--inline .role-switch__tab {
    gap: 4px;
    padding: 0 7px 0 5px;
    font-size: 12px;
  }

  .role-switch--inline .role-switch__icon {
    width: 20px;
    height: 20px;
    font-size: 13px;
  }
}

@media (max-width: 860px) {
  .role-switch--inline {
    display: none;
  }

  .role-switch--floating {
    position: fixed;
    z-index: 50;
    right: 12px;
    bottom: 10px;
    left: 12px;
    display: flex;
    padding: 6px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 14px 40px rgba(27, 29, 35, 0.18);
  }

  .role-switch--floating .role-switch__tab {
    flex: 1;
    justify-content: center;
    height: 46px;
    padding: 0 6px;
    font-size: 13px;
  }

  .role-switch--floating .role-switch__icon {
    width: 28px;
    height: 28px;
    font-size: 15px;
  }
}
</style>
