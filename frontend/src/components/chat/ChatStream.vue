<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { Headset, ShoppingBag, User } from '@element-plus/icons-vue'
import type { Message, Role } from '@/types/api'
import { formatChatTime, initials } from '@/utils/format'
import { senderLabels } from '@/utils/labels'

const props = withDefaults(
  defineProps<{
    messages: Message[]
    currentRole: Role
    emptyTitle?: string
    emptyDescription?: string
  }>(),
  {
    emptyTitle: '暂无消息',
    emptyDescription: '会话建立后，消息会显示在这里。',
  },
)

const scrollEl = ref<HTMLElement | null>(null)

const mineSender: Record<Role, string> = {
  consumer: 'customer',
  platform: 'platform',
  merchant: 'merchant',
}

function isMine(message: Message): boolean {
  return message.sender_type === mineSender[props.currentRole]
}

function displayName(message: Message): string {
  if (isMine(message)) return '我'
  return message.sender_name || senderLabels[message.sender_type] || '客服'
}

function avatarText(message: Message): string {
  if (message.sender_type === 'customer') {
    return initials(message.sender_name || '客')
  }
  return ''
}

function scrollToBottom(): void {
  nextTick(() => {
    if (!scrollEl.value) return
    scrollEl.value.scrollTop = scrollEl.value.scrollHeight
  })
}

watch(
  () => props.messages.length,
  () => scrollToBottom(),
)

onMounted(scrollToBottom)
</script>

<template>
  <div class="chat-stream">
    <div ref="scrollEl" class="chat-stream__scroll">
      <div v-if="messages.length === 0" class="chat-empty">
        <div class="chat-empty__icon">
          <el-icon><Headset /></el-icon>
        </div>
        <p>{{ emptyTitle }}</p>
        <span>{{ emptyDescription }}</span>
      </div>

      <template v-for="message in messages" :key="message.id">
        <div v-if="message.sender_type === 'system'" class="system-row">
          <span>{{ message.content }}</span>
          <time>{{ formatChatTime(message.created_at) }}</time>
        </div>

        <div
          v-else
          class="message-row"
          :class="{ 'is-mine': isMine(message) }"
        >
          <div
            v-if="!isMine(message)"
            class="message-avatar"
            :class="`is-${message.sender_type}`"
          >
            <el-icon v-if="message.sender_type === 'platform'"><Headset /></el-icon>
            <el-icon v-else-if="message.sender_type === 'merchant'"><ShoppingBag /></el-icon>
            <template v-else>{{ avatarText(message) }}</template>
          </div>

          <div class="message-content">
            <div class="message-meta">
              <span class="message-name">{{ displayName(message) }}</span>
              <span v-if="message.sender_type === 'platform'" class="role-label">平台</span>
              <span v-else-if="message.sender_type === 'merchant'" class="role-label is-merchant">商家</span>
              <time>{{ formatChatTime(message.created_at) }}</time>
            </div>
            <div class="message-bubble">{{ message.content }}</div>
          </div>

          <div
            v-if="isMine(message)"
            class="message-avatar is-owner"
            :class="`is-owner-${currentRole}`"
          >
            <el-icon v-if="currentRole === 'platform'"><Headset /></el-icon>
            <el-icon v-else-if="currentRole === 'merchant'"><ShoppingBag /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.chat-stream {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background:
    radial-gradient(circle at 18% 8%, color-mix(in srgb, var(--chat-accent, #ff5000) 5%, transparent), transparent 26%),
    linear-gradient(180deg, #fcfcfd 0%, #fafafb 100%);
}

.chat-stream__scroll {
  flex: 1;
  min-height: 0;
  padding: 22px 22px 18px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 240px;
  text-align: center;
}

.chat-empty__icon {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  margin-bottom: 14px;
  border: 1px solid color-mix(in srgb, var(--chat-accent, #ff5000) 22%, #ffffff);
  border-radius: 19px;
  color: var(--chat-accent, #ff5000);
  background: color-mix(in srgb, var(--chat-accent, #ff5000) 6%, #ffffff);
  font-size: 24px;
}

.chat-empty p {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.chat-empty span {
  max-width: 320px;
  margin-top: 7px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-muted);
}

.system-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  max-width: 82%;
  margin: 16px auto;
  text-align: center;
}

.system-row span {
  padding: 5px 12px;
  border-radius: 999px;
  color: #8d8d97;
  background: #f1f1f4;
  font-size: 13px;
  line-height: 1.6;
}

.system-row time {
  font-size: 12px;
  color: #b4b4bc;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-bottom: 18px;
}

.message-row.is-mine {
  justify-content: flex-end;
}

.message-avatar {
  display: grid;
  place-items: center;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  margin-top: 18px;
  border-radius: 11px;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.message-avatar.is-platform {
  background: linear-gradient(140deg, #6a9cf0, #2f6fe4);
}

.message-avatar.is-merchant {
  background: linear-gradient(140deg, #9db8a5, #7d9b84);
}

.message-avatar.is-customer {
  background: linear-gradient(140deg, #7b9bf1, #4a68ce);
}

.message-avatar.is-owner {
  background: linear-gradient(140deg, #c9a58f, #a8755f);
}

.message-avatar.is-owner.is-owner-consumer {
  background: linear-gradient(140deg, #c9a58f, #a8755f);
}

.message-avatar.is-owner.is-owner-merchant {
  background: linear-gradient(140deg, #9db8a5, #7d9b84);
}

.message-avatar.is-owner.is-owner-platform {
  background: linear-gradient(140deg, #6a9cf0, #2f6fe4);
}

.message-content {
  min-width: 0;
  max-width: min(74%, 620px);
}

.message-row.is-mine .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 18px;
  margin-bottom: 3px;
  color: var(--text-faint);
  font-size: 12px;
}

.message-row.is-mine .message-meta {
  flex-direction: row-reverse;
}

.message-name {
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
}

.role-label {
  padding: 1px 4px;
  border-radius: 3px;
  color: #2f6fe4;
  background: #eef4ff;
  font-size: 11px;
}

.role-label.is-merchant {
  color: #66816d;
  background: #eef5ef;
}

.message-bubble {
  padding: 10px 13px;
  border: 1px solid #ededf2;
  border-radius: 4px 14px 14px;
  color: #3b3b42;
  background: #fff;
  box-shadow: 0 4px 12px rgba(24, 26, 34, 0.035);
  font-size: 14px;
  line-height: 1.72;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.is-mine .message-bubble {
  border-color: transparent;
  border-radius: 14px 4px 14px 14px;
  color: #fff;
  background: linear-gradient(135deg, var(--chat-accent, #b07d62), var(--chat-accent-deep, #99664f));
  box-shadow: 0 8px 18px color-mix(in srgb, var(--chat-accent, #b07d62) 22%, transparent);
}

@media (max-width: 720px) {
  .chat-stream__scroll {
    padding: 16px 14px;
  }

  .message-content {
    max-width: 82%;
  }
}
</style>
