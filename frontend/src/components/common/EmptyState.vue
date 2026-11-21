<script setup lang="ts">
import { ChatDotRound } from '@element-plus/icons-vue'

withDefaults(
  defineProps<{
    title?: string
    description?: string
    compact?: boolean
  }>(),
  {
    title: '暂无内容',
    description: '',
    compact: false,
  },
)
</script>

<template>
  <div class="empty-state" :class="{ 'is-compact': compact }">
    <div class="empty-state__icon">
      <slot name="icon">
        <el-icon><ChatDotRound /></el-icon>
      </slot>
    </div>
    <p class="empty-state__title">{{ title }}</p>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
    <div v-if="$slots.default" class="empty-state__action">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  padding: 36px 24px;
  text-align: center;
}

.empty-state.is-compact {
  min-height: 170px;
  padding: 24px 16px;
}

.empty-state__icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  margin-bottom: 16px;
  border-radius: 18px;
  color: var(--brand);
  background: var(--brand-soft);
  font-size: 26px;
}

.is-compact .empty-state__icon {
  width: 44px;
  height: 44px;
  margin-bottom: 12px;
  border-radius: 14px;
  font-size: 20px;
}

.empty-state__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.empty-state__desc {
  max-width: 320px;
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.75;
  color: var(--text-muted);
}

.empty-state__action {
  margin-top: 16px;
}
</style>
