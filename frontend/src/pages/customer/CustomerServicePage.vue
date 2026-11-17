<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  CircleClose,
  Clock,
  Headset,
  Plus,
  Service,
} from '@element-plus/icons-vue'
import { useMockStore } from '@/stores/mock'
import { APP_NAME, APP_SUBTITLE, DEMO_AGENT_NAME } from '@/config'
import type { Conversation } from '@/types'
import { fromNow, initials, truncate } from '@/utils/format'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'

const mock = useMockStore()

const customer = computed(() => mock.currentCustomer)
const sessions = computed(() => mock.customerConversations())

const selectedId = ref<number | null>(sessions.value[0]?.id ?? null)
const draft = ref('')
const sendingConversationId = ref<number | null>(null)
const mobilePanel = ref<'list' | 'chat'>('chat')
const isMobile = ref(false)

const selectedConversation = computed<Conversation | undefined>(() => {
  if (selectedId.value == null) return undefined
  return mock.conversationById(selectedId.value)
})

const messages = computed(() =>
  selectedId.value == null ? [] : mock.messagesFor(selectedId.value),
)

const isAiTyping = computed(
  () =>
    selectedId.value != null &&
    mock.typingConversationId === selectedId.value,
)

const isSending = computed(
  () =>
    selectedId.value != null &&
    sendingConversationId.value === selectedId.value,
)

const isClosed = computed(() => selectedConversation.value?.status === 'closed')

const chatTitle = computed(() => {
  const conversation = selectedConversation.value
  if (!conversation) return '在线客服'
  if (conversation.status === 'ai') return '小橙 AI 助理'
  if (conversation.status === 'waiting') return '人工客服排队中'
  if (conversation.status === 'human') return conversation.agentName || DEMO_AGENT_NAME
  return '本次咨询已结束'
})

const chatSubtitle = computed(() => {
  const conversation = selectedConversation.value
  if (!conversation) return '选择或创建一个咨询会话'
  if (conversation.status === 'ai') return '智能售后助手 · 随时为你解答'
  if (conversation.status === 'waiting') {
    return `已进入人工队列 · ${fromNow(conversation.waitingSince)}转接`
  }
  if (conversation.status === 'human') return '人工客服在线 · 请放心沟通'
  return `会话 #${conversation.id} · ${fromNow(conversation.closedAt)}结束`
})

const composerPlaceholder = computed(() => {
  const status = selectedConversation.value?.status
  if (status === 'waiting') return '客服接入前，你可以先留言…'
  if (status === 'human') return '回复人工客服…'
  return '描述你的售后问题…'
})

const activeStatusText = computed(() => {
  const conversation = selectedConversation.value
  if (!conversation) return ''
  if (conversation.status === 'waiting') {
    return '已收到你的转人工请求，客服接入后会自动提醒，你的消息不会丢失。'
  }
  if (conversation.status === 'human') {
    return `人工客服${conversation.agentName || DEMO_AGENT_NAME}已接入，正在为你服务。`
  }
  if (conversation.status === 'closed') {
    return '本次会话已结束，如需继续咨询，请新建一个会话。'
  }
  return ''
})

let mediaQuery: MediaQueryList | null = null

function handleMediaChange(event: MediaQueryListEvent): void {
  isMobile.value = event.matches
  if (!event.matches) {
    mobilePanel.value = 'chat'
  }
}

onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 860px)')
  isMobile.value = mediaQuery.matches
  mobilePanel.value = mediaQuery.matches ? 'list' : 'chat'
  mediaQuery.addEventListener('change', handleMediaChange)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', handleMediaChange)
})

watch(
  () => sessions.value.length,
  () => {
    if (selectedId.value != null && !selectedConversation.value) {
      selectedId.value = sessions.value[0]?.id ?? null
    }
  },
)

function selectConversation(id: number): void {
  selectedId.value = id
  draft.value = ''
  if (isMobile.value) mobilePanel.value = 'chat'
}

function openConversationList(): void {
  mobilePanel.value = 'list'
}

function createNewConversation(): void {
  try {
    const conversation = mock.createConversation()
    selectedId.value = conversation.id
    draft.value = ''
    if (isMobile.value) mobilePanel.value = 'chat'
    ElMessage.success('已创建新的咨询会话')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '新建会话失败')
  }
}

async function handleSend(): Promise<void> {
  const conversation = selectedConversation.value
  const content = draft.value.trim()
  if (!conversation || !content || isClosed.value) return
  if (isSending.value || isAiTyping.value) return

  draft.value = ''
  sendingConversationId.value = conversation.id
  try {
    await mock.sendCustomerMessage(conversation.id, content)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '消息发送失败')
  } finally {
    if (sendingConversationId.value === conversation.id) {
      sendingConversationId.value = null
    }
  }
}

async function requestHuman(): Promise<void> {
  const conversation = selectedConversation.value
  if (!conversation || conversation.status !== 'ai') return

  try {
    mock.requestHuman(conversation.id)
    ElMessage.success('已提交人工客服请求，请稍候')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '转人工失败')
  }
}

async function closeConversation(): Promise<void> {
  const conversation = selectedConversation.value
  if (!conversation || conversation.status === 'closed') return

  try {
    await ElMessageBox.confirm(
      '结束后本次会话将只能查看历史记录，确定要结束吗？',
      '结束本次咨询',
      {
        confirmButtonText: '结束会话',
        cancelButtonText: '继续咨询',
        type: 'warning',
      },
    )
    mock.closeConversation(conversation.id, 'customer')
    ElMessage.success('会话已结束')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '操作失败')
    }
  }
}

function sessionSubtitle(conversation: Conversation): string {
  if (conversation.status === 'closed') {
    return truncate(conversation.lastMessage || '本次会话已结束', 44)
  }
  return truncate(conversation.lastMessage || '等待你的消息', 44)
}

function sessionStatusHint(conversation: Conversation): string {
  if (conversation.status === 'waiting') {
    return `已等待 ${fromNow(conversation.waitingSince).replace('前', '')}`
  }
  if (conversation.status === 'human') return conversation.agentName || DEMO_AGENT_NAME
  if (conversation.status === 'ai') return 'AI 智能接待'
  return '历史咨询'
}
</script>

<template>
  <div class="service-page">
    <header class="service-topbar">
      <router-link to="/service" class="brand">
        <span class="brand__mark">
          <el-icon><Headset /></el-icon>
        </span>
        <span class="brand__copy">
          <strong>{{ APP_NAME }}</strong>
          <small>{{ APP_SUBTITLE }}</small>
        </span>
      </router-link>

      <div class="service-topbar__center">
        <span class="online-dot" />
        客服在线 · 平均 30 秒响应
      </div>

      <div class="service-topbar__right">
        <span class="demo-pill">演示环境</span>
        <router-link to="/admin/workbench" class="workspace-link">
          客服工作台
        </router-link>
        <span class="user-chip">
          <span class="user-chip__avatar">{{ initials(customer.name) }}</span>
          <span>
            <strong>{{ customer.name }}</strong>
            <small>演示客户</small>
          </span>
        </span>
      </div>
    </header>

    <main class="service-main">
      <aside
        class="history-panel surface-card"
        :class="{ 'is-mobile-visible': mobilePanel === 'list' }"
      >
        <div class="history-head">
          <div>
            <p class="eyebrow">SERVICE CENTER</p>
            <h1>我的咨询</h1>
          </div>
          <span class="history-count">{{ sessions.length }}</span>
        </div>

        <button class="new-chat-button" type="button" @click="createNewConversation">
          <el-icon><Plus /></el-icon>
          新建咨询
        </button>

        <div class="history-list">
          <button
            v-for="conversation in sessions"
            :key="conversation.id"
            class="session-item"
            :class="{
              'is-active': conversation.id === selectedId,
              'is-waiting': conversation.status === 'waiting',
            }"
            type="button"
            @click="selectConversation(conversation.id)"
          >
            <div class="session-item__top">
              <span class="session-item__title">{{ conversation.title }}</span>
              <time>{{ fromNow(conversation.updatedAt) }}</time>
            </div>
            <p class="session-item__preview">{{ sessionSubtitle(conversation) }}</p>
            <div class="session-item__footer">
              <StatusTag kind="conversation" :value="conversation.status" dot />
              <span class="session-item__hint">{{ sessionStatusHint(conversation) }}</span>
            </div>
          </button>

          <EmptyState
            v-if="sessions.length === 0"
            compact
            title="还没有咨询记录"
            description="创建会话后，历史记录会保留在这里。"
          />
        </div>

        <div class="history-foot">
          <el-icon><Clock /></el-icon>
          <span>会话记录将在当前浏览器中保留</span>
        </div>
      </aside>

      <section
        class="chat-panel surface-card"
        :class="{ 'is-mobile-visible': mobilePanel === 'chat' }"
      >
        <template v-if="selectedConversation">
          <header class="chat-head">
            <button
              v-if="isMobile"
              class="mobile-back"
              type="button"
              aria-label="返回会话列表"
              @click="openConversationList"
            >
              <el-icon><ArrowLeft /></el-icon>
            </button>

            <div class="agent-avatar" :class="selectedConversation.status === 'human' ? 'is-human' : 'is-ai'">
              <el-icon v-if="selectedConversation.status === 'human'"><Headset /></el-icon>
              <el-icon v-else><Service /></el-icon>
              <span class="agent-avatar__status" />
            </div>

            <div class="chat-head__copy">
              <div class="chat-head__title-line">
                <h2>{{ chatTitle }}</h2>
                <StatusTag
                  kind="conversation"
                  :value="selectedConversation.status"
                  dot
                />
              </div>
              <p>{{ chatSubtitle }}</p>
            </div>

            <div class="chat-head__actions">
              <el-button
                v-if="selectedConversation.status === 'ai'"
                class="transfer-button"
                :icon="Headset"
                @click="requestHuman"
              >
                转人工
              </el-button>
              <span
                v-else-if="selectedConversation.status === 'waiting'"
                class="queue-chip"
              >
                <i />
                排队中
              </span>
              <button
                v-if="selectedConversation.status !== 'closed'"
                class="quiet-action"
                type="button"
                title="结束本次会话"
                aria-label="结束本次会话"
                @click="closeConversation"
              >
                <el-icon><CircleClose /></el-icon>
                <span class="quiet-action__label">结束</span>
              </button>
            </div>
          </header>

          <div
            v-if="selectedConversation.status !== 'ai'"
            class="service-banner"
            :class="`is-${selectedConversation.status}`"
          >
            <span class="service-banner__dot" />
            <span>{{ activeStatusText }}</span>
            <span v-if="selectedConversation.status === 'waiting'" class="queue-pulse">
              <i /><i /><i />
            </span>
          </div>

          <ChatStream
            :key="selectedConversation.id"
            :messages="messages"
            perspective="customer"
            :customer-name="customer.name"
            :agent-name="selectedConversation.agentName || DEMO_AGENT_NAME"
            :typing="isAiTyping"
            typing-label="小橙正在组织回复…"
          />

          <div v-if="isClosed" class="closed-composer">
            <div>
              <span class="closed-composer__icon"><el-icon><CircleClose /></el-icon></span>
              <div>
                <p>本次会话已结束</p>
                <small>如需继续咨询，请创建一个新的会话</small>
              </div>
            </div>
            <el-button type="primary" @click="createNewConversation">
              新建咨询
            </el-button>
          </div>
          <ChatComposer
            v-else
            v-model="draft"
            :disabled="isSending"
            :loading="isSending"
            :placeholder="composerPlaceholder"
            @send="handleSend"
          />
        </template>

        <EmptyState
          v-else
          title="选择或创建一个会话"
          description="你的历史咨询会显示在左侧，也可以立即发起新的售后咨询。"
        >
          <el-button type="primary" :icon="Plus" @click="createNewConversation">
            新建咨询
          </el-button>
        </EmptyState>
      </section>
    </main>
  </div>
</template>

<style scoped>
.service-page {
  --chat-accent: #ff6a13;
  --chat-accent-deep: #f14b00;
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background:
    radial-gradient(circle at 6% -8%, rgba(255, 133, 52, 0.18), transparent 28%),
    radial-gradient(circle at 94% 8%, rgba(255, 196, 146, 0.2), transparent 24%),
    linear-gradient(180deg, #fbfaf9 0%, #f5f6f8 260px, #f5f6f8 100%);
}

.service-page::before {
  content: '';
  position: absolute;
  top: -120px;
  left: 50%;
  width: 900px;
  height: 260px;
  border-radius: 50%;
  background: rgba(255, 100, 20, 0.06);
  filter: blur(70px);
  transform: translateX(-50%);
  pointer-events: none;
}

.service-topbar {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  flex: 0 0 72px;
  width: min(1240px, calc(100% - 40px));
  margin: 0 auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
}

.brand__mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 13px;
  color: #fff;
  background: linear-gradient(145deg, #ff8c2f 0%, #ff5000 58%, #ef3f00 100%);
  box-shadow:
    0 8px 18px rgba(255, 80, 0, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
  font-size: 21px;
}

.brand__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand__copy strong {
  color: #202024;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand__copy small {
  color: #9999a3;
  font-size: 10px;
  letter-spacing: 0.06em;
}

.service-topbar__center {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-left: 28px;
  padding-left: 22px;
  border-left: 1px solid rgba(214, 214, 220, 0.8);
  color: #85858f;
  font-size: 11px;
}

.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #14b87a;
  box-shadow: 0 0 0 3px rgba(20, 184, 122, 0.13);
}

.service-topbar__right {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-left: auto;
}

.demo-pill {
  padding: 3px 8px;
  border: 1px solid #ffe0d0;
  border-radius: 5px;
  color: #f06822;
  background: rgba(255, 248, 243, 0.88);
  font-size: 10px;
  font-weight: 600;
}

.workspace-link {
  color: #7f7f89;
  font-size: 12px;
  transition: color 0.2s ease;
}

.workspace-link:hover {
  color: var(--brand);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 7px 5px 5px;
  border: 1px solid rgba(229, 229, 234, 0.9);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
}

.user-chip__avatar {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  background: linear-gradient(145deg, #ffa35d, #ff5e12);
  font-size: 12px;
  font-weight: 700;
}

.user-chip > span:last-child {
  display: flex;
  flex-direction: column;
  padding-right: 6px;
  line-height: 1.25;
}

.user-chip strong {
  color: #4d4d55;
  font-size: 11px;
  font-weight: 600;
}

.user-chip small {
  color: #a2a2ab;
  font-size: 9px;
}

.service-main {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 324px minmax(0, 1fr);
  gap: 18px;
  flex: 1;
  width: min(1240px, calc(100% - 40px));
  min-height: 0;
  margin: 0 auto 22px;
}

.history-panel,
.chat-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.history-panel {
  padding: 20px 14px 12px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(14px);
}

.history-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 2px 8px 15px;
}

.history-head h1 {
  margin-top: 4px;
  color: #25252b;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.history-count {
  display: grid;
  place-items: center;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 7px;
  color: #a0a0aa;
  background: #f5f5f8;
  font-size: 11px;
  font-weight: 600;
}

.new-chat-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex: 0 0 auto;
  width: calc(100% - 4px);
  height: 40px;
  margin: 0 2px 11px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, #ff7a25, #ff5000);
  box-shadow: 0 8px 18px rgba(255, 80, 0, 0.19);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease;
}

.new-chat-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 11px 22px rgba(255, 80, 0, 0.25);
}

.history-list {
  flex: 1;
  min-height: 0;
  padding: 2px;
  overflow-y: auto;
}

.session-item {
  position: relative;
  display: block;
  width: 100%;
  margin-bottom: 6px;
  padding: 12px 12px 11px;
  border: 1px solid transparent;
  border-radius: 11px;
  text-align: left;
  background: transparent;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}

.session-item:hover {
  background: #fafafb;
}

.session-item.is-active {
  border-color: #ffe1d0;
  background: linear-gradient(145deg, #fff8f3, #fff3ea);
  box-shadow: inset 3px 0 0 #ff5a0a;
}

.session-item.is-waiting:not(.is-active) {
  border-color: #fff1da;
}

.session-item__top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-item__title {
  flex: 1;
  overflow: hidden;
  color: #35353b;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-item__top time {
  flex: 0 0 auto;
  color: #adadb6;
  font-size: 10px;
}

.session-item__preview {
  display: -webkit-box;
  margin-top: 5px;
  overflow: hidden;
  color: #9b9ba5;
  font-size: 12px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.session-item__footer {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 8px;
}

.session-item__footer :deep(.status-tag) {
  height: 19px;
  padding: 0 6px;
  border-radius: 5px;
  font-size: 10px;
}

.session-item__hint {
  color: #b1b1ba;
  font-size: 10px;
}

.history-foot {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
  padding: 11px 9px 2px;
  border-top: 1px solid #f2f2f5;
  color: #b1b1b9;
  font-size: 10px;
}

.chat-panel {
  position: relative;
  background: #fff;
}

.chat-head {
  display: flex;
  align-items: center;
  gap: 11px;
  flex: 0 0 auto;
  min-height: 72px;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f4;
  background: linear-gradient(180deg, #fffdfb, #ffffff);
}

.mobile-back {
  display: none;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  color: #6c6c76;
  background: #f5f5f8;
  font-size: 16px;
  cursor: pointer;
}

.agent-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  color: #fff;
  background: linear-gradient(145deg, #ff9a45, #ff5a12);
  box-shadow: 0 8px 18px rgba(255, 90, 18, 0.19);
  font-size: 20px;
}

.agent-avatar.is-human {
  background: linear-gradient(145deg, #ff8a44, #ee4d1d);
}

.agent-avatar__status {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 10px;
  height: 10px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #12b97a;
}

.chat-head__copy {
  min-width: 0;
}

.chat-head__title-line {
  display: flex;
  align-items: center;
  gap: 9px;
}

.chat-head__title-line h2 {
  overflow: hidden;
  color: #26262c;
  font-size: 15px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-head__copy p {
  margin-top: 5px;
  color: #9c9ca6;
  font-size: 11px;
}

.chat-head__actions {
  display: flex;
  align-items: center;
  gap: 13px;
  margin-left: auto;
}

.transfer-button {
  height: 32px;
  border-color: #ffd6c1;
  border-radius: 8px;
  color: #f15a10;
  background: #fff8f3;
  font-size: 12px;
}

.transfer-button:hover {
  border-color: #ffb58c;
  color: #e54b00;
  background: #fff3ea;
}

.queue-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid #ffe2ba;
  border-radius: 8px;
  color: #c37900;
  background: #fff9ed;
  font-size: 10px;
  font-weight: 600;
}

.queue-chip i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f0a000;
  animation: queue-blink 1.4s ease-in-out infinite;
}

.quiet-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 2px;
  color: #a0a0aa;
  background: transparent;
  font-size: 11px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.quiet-action:hover {
  color: #e15a4d;
}

.service-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
  min-height: 36px;
  padding: 8px 20px;
  border-bottom: 1px solid transparent;
  font-size: 12px;
}

.service-banner.is-waiting {
  color: #a96a00;
  border-color: #fff0d2;
  background: #fffaf0;
}

.service-banner.is-human {
  color: #0d8c61;
  border-color: #d9f5e8;
  background: #f3fcf8;
}

.service-banner.is-closed {
  color: #82828c;
  border-color: #efeff3;
  background: #fafafb;
}

.service-banner__dot {
  flex: 0 0 auto;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

.queue-pulse {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: 3px;
}

.queue-pulse i {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #e9a300;
  animation: typing-dot 1s infinite ease-in-out;
}

.queue-pulse i:nth-child(2) {
  animation-delay: 0.12s;
}

.queue-pulse i:nth-child(3) {
  animation-delay: 0.24s;
}

.closed-composer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex: 0 0 auto;
  padding: 14px 20px;
  border-top: 1px solid #f0f0f4;
  background: #fbfbfc;
}

.closed-composer > div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.closed-composer__icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #a3a3ad;
  background: #f2f2f5;
  font-size: 17px;
}

.closed-composer p {
  color: #5d5d66;
  font-size: 12px;
  font-weight: 600;
}

.closed-composer small {
  display: block;
  margin-top: 2px;
  color: #a4a4ad;
  font-size: 10px;
}

@keyframes typing-dot {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  30% {
    transform: translateY(-2px);
    opacity: 1;
  }
}

@keyframes queue-blink {
  0%,
  100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

@media (max-width: 1000px) {
  .service-main {
    grid-template-columns: 282px minmax(0, 1fr);
  }

  .service-topbar__center {
    display: none;
  }
}

@media (max-width: 860px) {
  .service-page {
    background: #f6f7f9;
  }

  .service-topbar {
    flex-basis: 60px;
    width: calc(100% - 24px);
  }

  .service-topbar__right {
    gap: 8px;
  }

  .demo-pill,
  .workspace-link,
  .user-chip > span:last-child {
    display: none;
  }

  .service-main {
    display: block;
    width: calc(100% - 20px);
    margin-bottom: 10px;
  }

  .history-panel,
  .chat-panel {
    display: none;
    width: 100%;
    height: 100%;
    border-radius: 15px;
  }

  .history-panel.is-mobile-visible,
  .chat-panel.is-mobile-visible {
    display: flex;
  }

  .mobile-back {
    display: grid;
  }

  .chat-head {
    min-height: 66px;
    padding: 10px 12px;
  }

  .agent-avatar {
    flex-basis: 36px;
    width: 36px;
    height: 36px;
    border-radius: 11px;
    font-size: 17px;
  }

  .chat-head__title-line h2 {
    font-size: 13px;
  }

  .chat-head__copy p {
    max-width: 160px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .chat-head__actions {
    gap: 8px;
  }

  .quiet-action {
    padding: 6px;
    font-size: 14px;
  }

  .quiet-action__label {
    display: none;
  }

  .chat-head__title-line {
    gap: 6px;
  }

  .chat-head__title-line :deep(.status-tag) {
    display: none;
  }

  .transfer-button {
    padding: 0 9px;
    font-size: 10px;
  }

  .service-banner {
    padding: 8px 13px;
    font-size: 10px;
    line-height: 1.5;
  }

  .closed-composer {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .brand__copy small {
    display: none;
  }

  .service-topbar__right .user-chip {
    border-color: transparent;
    background: transparent;
  }

  .history-panel {
    padding: 16px 10px 8px;
  }

  .queue-chip {
    display: none;
  }
}
</style>
