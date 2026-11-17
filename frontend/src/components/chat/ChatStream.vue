<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { Cpu, Headset, MagicStick } from '@element-plus/icons-vue'
import type { ChatMessage } from '@/types'
import { formatChatTime, initials } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    messages: ChatMessage[]
    perspective: 'customer' | 'agent'
    customerName: string
    agentName?: string
    typing?: boolean
    typingLabel?: string
    emptyTitle?: string
    emptyDescription?: string
  }>(),
  {
    agentName: '人工客服',
    typing: false,
    typingLabel: '小橙正在输入…',
    emptyTitle: '还没有消息',
    emptyDescription: '发送一条消息，开始本次售后咨询。',
  },
)

const scrollEl = ref<HTMLElement | null>(null)

const isMine = (message: ChatMessage): boolean => {
  if (props.perspective === 'customer') return message.senderType === 'customer'
  return message.senderType === 'agent'
}

const senderName = (message: ChatMessage): string => {
  if (message.senderType === 'customer') {
    return props.perspective === 'customer' ? '我' : props.customerName
  }
  if (message.senderType === 'ai') return '小橙 AI 助理'
  if (message.senderType === 'agent') return props.agentName || '人工客服'
  return ''
}

function scrollToBottom(): void {
  nextTick(() => {
    if (!scrollEl.value) return
    scrollEl.value.scrollTop = scrollEl.value.scrollHeight
  })
}

watch(
  () => [props.messages.length, props.typing],
  () => scrollToBottom(),
)

onMounted(scrollToBottom)
</script>

<template>
  <div class="chat-stream">
    <div ref="scrollEl" class="chat-stream__scroll">
      <div v-if="messages.length === 0 && !typing" class="chat-stream__empty">
        <div class="empty-orb">
          <el-icon><MagicStick /></el-icon>
        </div>
        <p>{{ emptyTitle }}</p>
        <span>{{ emptyDescription }}</span>
      </div>

      <template v-for="message in messages" :key="message.id">
        <div v-if="message.senderType === 'system'" class="system-row">
          <span>{{ message.content }}</span>
          <time>{{ formatChatTime(message.createdAt) }}</time>
        </div>

        <div
          v-else
          class="message-row"
          :class="{
            'is-mine': isMine(message),
            'is-ai': message.senderType === 'ai',
          }"
        >
          <div
            v-if="!isMine(message)"
            class="message-avatar"
            :class="message.senderType === 'ai' ? 'is-ai' : 'is-customer'"
          >
            <el-icon v-if="message.senderType === 'ai'"><Cpu /></el-icon>
            <el-icon v-else-if="message.senderType === 'agent'"><Headset /></el-icon>
            <span v-else>{{ initials(customerName) }}</span>
          </div>

          <div class="message-content">
            <div class="message-meta">
              <span class="message-name">{{ senderName(message) }}</span>
              <span v-if="message.senderType === 'ai'" class="ai-label">AI</span>
              <time>{{ formatChatTime(message.createdAt) }}</time>
            </div>
            <div class="message-bubble">
              {{ message.content }}
            </div>
          </div>

          <div v-if="isMine(message)" class="message-avatar is-owner">
            <span>{{ perspective === 'customer' ? initials(customerName) : '橙' }}</span>
          </div>
        </div>
      </template>

      <div v-if="typing" class="message-row is-ai typing-row">
        <div class="message-avatar is-ai">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="message-content">
          <div class="message-meta">
            <span class="message-name">小橙 AI 助理</span>
            <span class="ai-label">AI</span>
          </div>
          <div class="message-bubble typing-bubble">
            <span class="typing-dots"><i /><i /><i /></span>
            <span class="typing-text">{{ typingLabel }}</span>
          </div>
        </div>
      </div>
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
    radial-gradient(circle at 18% 8%, rgba(255, 120, 43, 0.045), transparent 26%),
    linear-gradient(180deg, #fcfcfd 0%, #fafafb 100%);
}

.chat-stream__scroll {
  flex: 1;
  min-height: 0;
  padding: 20px 22px 18px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.chat-stream__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 220px;
  text-align: center;
}

.empty-orb {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  margin-bottom: 14px;
  border: 1px solid #ffe0ce;
  border-radius: 19px;
  color: var(--brand);
  background: linear-gradient(145deg, #fff7f1, #fff0e6);
  font-size: 24px;
  box-shadow: 0 12px 28px rgba(255, 80, 0, 0.1);
}

.chat-stream__empty p {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.chat-stream__empty span {
  max-width: 300px;
  margin-top: 7px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-muted);
}

.system-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin: 16px auto;
  max-width: 80%;
  text-align: center;
}

.system-row span {
  padding: 5px 12px;
  border-radius: 999px;
  color: #8d8d97;
  background: #f1f1f4;
  font-size: 12px;
  line-height: 1.5;
}

.system-row time {
  font-size: 10px;
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

.message-avatar.is-ai {
  background: linear-gradient(140deg, #ff9a45, #ff5b14);
  box-shadow: 0 5px 12px rgba(255, 91, 20, 0.2);
}

.message-avatar.is-customer {
  background: linear-gradient(140deg, #789cf5, #4c6de0);
}

.message-avatar.is-owner {
  background: linear-gradient(140deg, #ff9a45, #ff5b14);
}

.is-mine .message-avatar.is-owner {
  margin-left: 2px;
}

.message-content {
  min-width: 0;
  max-width: min(76%, 600px);
}

.is-mine .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 18px;
  margin-bottom: 3px;
  font-size: 11px;
  color: var(--text-faint);
}

.is-mine .message-meta {
  flex-direction: row-reverse;
}

.message-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.ai-label {
  padding: 1px 4px;
  border: 1px solid #ffd8c1;
  border-radius: 4px;
  color: var(--brand);
  background: #fff8f4;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.04em;
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

.is-mine .message-bubble {
  border-color: transparent;
  border-radius: 14px 4px 14px 14px;
  color: #fff;
  background: linear-gradient(135deg, var(--chat-accent, #ff6a13), var(--chat-accent-deep, #f14b00));
  box-shadow: 0 8px 18px rgba(241, 75, 0, 0.16);
}

.is-ai .message-bubble {
  border-color: #ffe6d8;
  background: linear-gradient(180deg, #fffdfb, #fff9f5);
}

.typing-row {
  margin-bottom: 2px;
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 38px;
}

.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.typing-dots i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ff9560;
  animation: typing-bounce 1.1s ease-in-out infinite;
}

.typing-dots i:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots i:nth-child(3) {
  animation-delay: 0.3s;
}

.typing-text {
  color: var(--text-muted);
  font-size: 11px;
}

@keyframes typing-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  30% {
    transform: translateY(-3px);
    opacity: 1;
  }
}

@media (max-width: 720px) {
  .chat-stream__scroll {
    padding: 16px 14px;
  }

  .message-content {
    max-width: 82%;
  }

  .message-avatar {
    flex-basis: 30px;
    width: 30px;
    height: 30px;
  }
}
</style>
