<script setup lang="ts">
import { computed } from 'vue'
import {
  getConversationStatus,
  getOrderStatus,
  getPriority,
  getTicketStatus,
  type Meta,
} from '@/utils/labels'

const props = withDefaults(
  defineProps<{
    kind: 'conversation' | 'order' | 'ticket' | 'priority'
    value: string
    dot?: boolean
  }>(),
  {
    dot: false,
  },
)

const meta = computed<Meta>(() => {
  if (props.kind === 'conversation') return getConversationStatus(props.value)
  if (props.kind === 'order') return getOrderStatus(props.value)
  if (props.kind === 'ticket') return getTicketStatus(props.value)
  return getPriority(props.value)
})
</script>

<template>
  <span class="status-tag" :class="[`tone-${meta.tone}`, { 'has-dot': dot }]">
    <i v-if="dot" class="status-tag__dot" aria-hidden="true" />
    {{ meta.label }}
  </span>
</template>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 22px;
  padding: 0 8px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
}

.status-tag__dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

.tone-blue {
  color: #2f6fe4;
  background: #eef4ff;
  border-color: #dce8ff;
}

.tone-amber {
  color: #c97900;
  background: #fff7e6;
  border-color: #ffebc2;
}

.tone-green {
  color: #0b8b60;
  background: #eaf9f2;
  border-color: #d4f2e4;
}

.tone-gray {
  color: #777782;
  background: #f5f5f8;
  border-color: #ebebf0;
}

.tone-red {
  color: #d52b24;
  background: #fff0ef;
  border-color: #ffdedb;
}

.tone-orange {
  color: #dc6800;
  background: #fff3e8;
  border-color: #ffe1c7;
}

.tone-violet {
  color: #7354cd;
  background: #f4f0ff;
  border-color: #e8e0ff;
}
</style>
