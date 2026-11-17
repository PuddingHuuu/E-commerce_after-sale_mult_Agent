<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowRight,
  Box,
  ChatDotRound,
  CircleClose,
  Clock,
  Headset,
  Phone,
  Plus,
  Search,
  Tickets,
} from '@element-plus/icons-vue'
import type { Conversation, ConversationStatus } from '@/types'
import { useMockStore } from '@/stores/mock'
import { useAdminUiStore } from '@/stores/adminUi'
import { DEMO_AGENT_NAME } from '@/config'
import {
  formatAmount,
  formatDateTime,
  fromNow,
  humanDuration,
  initials,
  maskPhone,
  truncate,
} from '@/utils/format'
import { ticketTypeLabel } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'

type TabKey = Extract<ConversationStatus, 'waiting' | 'human' | 'closed'>

const route = useRoute()
const router = useRouter()
const mock = useMockStore()
const ui = useAdminUiStore()

const tabs: { key: TabKey; label: string }[] = [
  { key: 'waiting', label: '待接入' },
  { key: 'human', label: '服务中' },
  { key: 'closed', label: '已结束' },
]

const activeTab = ref<TabKey>('waiting')
const keyword = ref('')
const selectedId = ref<number | null>(null)
const draft = ref('')

const serviceSessions = computed(() =>
  mock.db.conversations.filter((item) => item.status !== 'ai'),
)

const tabCounts = computed<Record<TabKey, number>>(() => ({
  waiting: serviceSessions.value.filter((item) => item.status === 'waiting').length,
  human: serviceSessions.value.filter((item) => item.status === 'human').length,
  closed: serviceSessions.value.filter((item) => item.status === 'closed').length,
}))

function sessionsInTab(tab: TabKey): Conversation[] {
  return serviceSessions.value
    .filter((conversation) => conversation.status === tab)
    .sort((a, b) => {
      if (tab === 'waiting') {
        if (!a.waitingSince || !b.waitingSince) return a.id - b.id
        return new Date(a.waitingSince).getTime() - new Date(b.waitingSince).getTime()
      }
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    })
}

const filteredSessions = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  const list = sessionsInTab(activeTab.value)
  if (!term) return list

  return list.filter((conversation) => {
    const customer = mock.customerById(conversation.customerId)
    return [
      String(conversation.id),
      conversation.title,
      conversation.lastMessage,
      customer?.name ?? '',
      customer?.phone ?? '',
    ]
      .join(' ')
      .toLowerCase()
      .includes(term)
  })
})

const selectedConversation = computed<Conversation | undefined>(() =>
  selectedId.value == null ? undefined : mock.conversationById(selectedId.value),
)

const customer = computed(() =>
  selectedConversation.value
    ? mock.customerById(selectedConversation.value.customerId)
    : undefined,
)

const messages = computed(() =>
  selectedConversation.value ? mock.messagesFor(selectedConversation.value.id) : [],
)

const customerOrders = computed(() =>
  customer.value ? mock.ordersForCustomer(customer.value.id) : [],
)

const customerTickets = computed(() =>
  customer.value ? mock.ticketsForCustomer(customer.value.id) : [],
)

const recentOrders = computed(() => customerOrders.value.slice(0, 3))
const recentTickets = computed(() => customerTickets.value.slice(0, 3))

const isWaiting = computed(() => selectedConversation.value?.status === 'waiting')
const isHuman = computed(() => selectedConversation.value?.status === 'human')
const isClosed = computed(() => selectedConversation.value?.status === 'closed')

const currentWaitingTime = computed(() =>
  selectedConversation.value?.waitingSince
    ? humanDuration(selectedConversation.value.waitingSince)
    : '—',
)

function conversationCustomer(conversation: Conversation) {
  return mock.customerById(conversation.customerId)
}

function selectConversation(id: number, updateQuery = true): void {
  selectedId.value = id
  draft.value = ''
  const conversation = mock.conversationById(id)
  if (conversation && conversation.status !== 'ai') {
    activeTab.value = conversation.status
  }
  if (updateQuery && route.query.session !== String(id)) {
    router.replace({
      name: 'admin-workbench',
      query: { ...route.query, session: String(id) },
    })
  }
}

function initialSelection(): void {
  const candidates = [
    sessionsInTab('waiting')[0],
    sessionsInTab('human')[0],
    sessionsInTab('closed')[0],
  ].filter(Boolean) as Conversation[]
  const first = candidates[0]
  if (first) {
    activeTab.value = first.status as TabKey
    selectedId.value = first.id
  }
}

function syncSelectionFromRoute(): void {
  const raw = route.query.session
  const value = Array.isArray(raw) ? raw[0] : raw
  if (!value) {
    if (selectedId.value == null) initialSelection()
    return
  }
  const id = Number(value)
  const conversation = Number.isFinite(id) ? mock.conversationById(id) : undefined
  if (conversation && conversation.status !== 'ai') {
    activeTab.value = conversation.status
    selectedId.value = conversation.id
    draft.value = ''
    return
  }
  if (selectedId.value == null) initialSelection()
}

watch(() => route.query.session, syncSelectionFromRoute, { immediate: true })

watch(filteredSessions, (list) => {
  if (!selectedConversation.value && list[0]) {
    selectConversation(list[0].id)
  }
})

function switchTab(tab: TabKey): void {
  activeTab.value = tab
  const current = selectedConversation.value
  if (current && current.status === tab) return

  keyword.value = ''
  const first = sessionsInTab(tab)[0]
  if (first) {
    selectConversation(first.id)
  } else {
    selectedId.value = null
    draft.value = ''
  }
}

function acceptCurrent(): void {
  if (!selectedConversation.value) return
  try {
    mock.acceptConversation(selectedConversation.value.id)
    activeTab.value = 'human'
    ElMessage.success('会话已接入，现在可以回复客户了')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '接入会话失败')
  }
}

function sendReply(): void {
  if (!selectedConversation.value || !isHuman.value) return
  const content = draft.value.trim()
  if (!content) return
  try {
    mock.sendAgentMessage(selectedConversation.value.id, content)
    draft.value = ''
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '消息发送失败')
  }
}

async function closeCurrent(): Promise<void> {
  if (!selectedConversation.value || isClosed.value) return
  try {
    await ElMessageBox.confirm(
      '结束会话后客户将无法继续回复，确定要结束当前会话吗？',
      '结束会话',
      {
        confirmButtonText: '结束会话',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    mock.closeConversation(selectedConversation.value.id, 'agent')
    activeTab.value = 'closed'
    ElMessage.success('会话已结束')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '结束会话失败')
    }
  }
}

function createTicket(): void {
  if (!selectedConversation.value || !customer.value) return
  ui.openCreateTicket({
    customerId: customer.value.id,
    conversationId: selectedConversation.value.id,
    orderId: customerOrders.value[0]?.id ?? null,
  })
}

function openAllOrders(): void {
  if (!customer.value) return
  router.push({
    name: 'admin-orders',
    query: { keyword: customer.value.name },
  })
}

function openAllTickets(): void {
  if (!customer.value) return
  router.push({
    name: 'admin-tickets',
    query: { keyword: customer.value.name },
  })
}

function sessionHint(conversation: Conversation): string {
  if (conversation.status === 'waiting') {
    return `等待 ${humanDuration(conversation.waitingSince)}`
  }
  if (conversation.status === 'human') {
    return conversation.agentName || '人工服务中'
  }
  return fromNow(conversation.closedAt || conversation.updatedAt)
}
</script>

<template>
  <div class="workbench-page">
    <header class="workbench-head">
      <div>
        <p class="eyebrow">UNIFIED INBOX</p>
        <div class="workbench-title-line">
          <h1 class="page-title">售后工作台</h1>
          <span class="live-badge"><i /> 实时同步</span>
        </div>
        <p class="page-desc">
          集中处理转人工会话，在同一工作区查看客户、订单与工单上下文。
        </p>
      </div>
      <div class="workbench-head__summary">
        <div>
          <span>待接入</span>
          <strong>{{ tabCounts.waiting }}</strong>
        </div>
        <div>
          <span>服务中</span>
          <strong>{{ tabCounts.human }}</strong>
        </div>
        <div>
          <span>已结束</span>
          <strong>{{ tabCounts.closed }}</strong>
        </div>
      </div>
    </header>

    <div class="workbench-grid">
      <aside class="queue-panel panel-surface">
        <div class="queue-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            :class="{ 'is-active': activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            <span>{{ tab.label }}</span>
            <em>{{ tabCounts[tab.key] }}</em>
          </button>
        </div>

        <div class="queue-search">
          <el-input
            v-model="keyword"
            size="small"
            :prefix-icon="Search"
            placeholder="搜索客户、会话或消息"
            clearable
          />
        </div>

        <div class="queue-list">
          <button
            v-for="conversation in filteredSessions"
            :key="conversation.id"
            type="button"
            class="queue-item"
            :class="{
              'is-active': conversation.id === selectedId,
              'is-waiting': conversation.status === 'waiting',
            }"
            @click="selectConversation(conversation.id)"
          >
            <span class="queue-avatar">
              {{ initials(conversationCustomer(conversation)?.name || '客') }}
              <i v-if="conversation.status === 'waiting'" />
            </span>
            <span class="queue-body">
              <span class="queue-topline">
                <strong>{{ conversationCustomer(conversation)?.name || '客户' }}</strong>
                <time>{{ fromNow(conversation.updatedAt) }}</time>
              </span>
              <span class="queue-title">{{ conversation.title }}</span>
              <span class="queue-preview">{{ truncate(conversation.lastMessage || '暂无消息', 36) }}</span>
              <span class="queue-footline">
                <StatusTag
                  kind="conversation"
                  :value="conversation.status"
                  dot
                />
                <em>{{ sessionHint(conversation) }}</em>
                <i v-if="conversation.status === 'waiting'" class="waiting-pulse" />
              </span>
            </span>
          </button>

          <EmptyState
            v-if="filteredSessions.length === 0"
            compact
            :title="keyword ? '没有匹配的会话' : '当前队列为空'"
            :description="
              keyword
                ? '换个关键词试试，或清空搜索条件。'
                : activeTab === 'waiting'
                  ? '客户点击「转人工」后，会话会出现在这里。'
                  : '暂无该状态的会话。'
            "
          />
        </div>
      </aside>

      <section class="conversation-panel panel-surface">
        <template v-if="selectedConversation && customer">
          <header class="conversation-head">
            <span class="conversation-avatar">
              {{ initials(customer.name) }}
              <i />
            </span>
            <div class="conversation-head__copy">
              <div class="conversation-head__title">
                <h2>{{ customer.name }}</h2>
                <StatusTag
                  kind="conversation"
                  :value="selectedConversation.status"
                  dot
                />
                <span v-if="isWaiting" class="waiting-timer">
                  <el-icon><Clock /></el-icon>
                  已等待 {{ currentWaitingTime }}
                </span>
              </div>
              <p>
                {{ maskPhone(customer.phone) }}
                <span>·</span>
                会话 #{{ selectedConversation.id }}
                <span>·</span>
                创建于 {{ formatDateTime(selectedConversation.createdAt) }}
              </p>
            </div>
            <div class="conversation-actions">
              <el-button
                v-if="isWaiting"
                type="primary"
                :icon="Headset"
                @click="acceptCurrent"
              >
                接入会话
              </el-button>
              <el-button :icon="Tickets" @click="createTicket">创建工单</el-button>
              <button
                v-if="!isClosed"
                class="conversation-close"
                type="button"
                @click="closeCurrent"
              >
                <el-icon><CircleClose /></el-icon>
                结束
              </button>
            </div>
          </header>

          <div v-if="isWaiting" class="awaiting-banner">
            <span class="awaiting-banner__icon"><el-icon><Headset /></el-icon></span>
            <div>
              <strong>客户正在等待人工接入</strong>
              <p>接入后即可回复。接入前的客户留言会保留在对话中。</p>
            </div>
            <el-button size="small" type="primary" @click="acceptCurrent">
              立即接入
            </el-button>
          </div>

          <div v-if="isClosed" class="closed-banner">
            <el-icon><CircleClose /></el-icon>
            <span>本次会话已结束，该会话仅支持查看与创建工单。</span>
          </div>

          <ChatStream
            :key="selectedConversation.id"
            :messages="messages"
            perspective="agent"
            :customer-name="customer.name"
            :agent-name="selectedConversation.agentName || DEMO_AGENT_NAME"
            empty-title="暂无聊天记录"
            empty-description="等待客户发送消息，或查看右侧客户上下文。"
          />

          <ChatComposer
            v-if="isHuman"
            v-model="draft"
            placeholder="输入回复，Enter 发送…"
            @send="sendReply"
          />
          <div v-else-if="isWaiting" class="conversation-footnote">
            <span>请先接入会话，再向客户发送回复</span>
            <el-button size="small" type="primary" :icon="Headset" @click="acceptCurrent">
              接入
            </el-button>
          </div>
          <div v-else class="conversation-footnote is-closed">
            <el-icon><CircleClose /></el-icon>
            会话已结束，无法继续发送消息
          </div>
        </template>

        <EmptyState
          v-else
          title="选择一段会话"
          description="从左侧待接入或服务中的队列选择会话，开始处理客户售后请求。"
        />
      </section>

      <aside v-if="customer && selectedConversation" class="context-panel">
        <div class="context-card customer-card">
          <div class="customer-card__head">
            <span class="customer-card__avatar">{{ initials(customer.name) }}</span>
            <div>
              <div class="customer-card__name">
                <h3>{{ customer.name }}</h3>
                <span class="demo-label">演示客户</span>
              </div>
              <p>客户 ID · C{{ String(customer.id).padStart(4, '0') }}</p>
            </div>
          </div>
          <div class="customer-card__meta">
            <span><el-icon><Phone /></el-icon>{{ maskPhone(customer.phone) }}</span>
            <span><el-icon><Clock /></el-icon>加入于 {{ formatDateTime(customer.joinedAt) }}</span>
          </div>
          <div class="customer-card__stats">
            <div>
              <strong>{{ customerOrders.length }}</strong>
              <span>历史订单</span>
            </div>
            <div>
              <strong>{{ customerTickets.length }}</strong>
              <span>售后工单</span>
            </div>
            <div>
              <strong>{{ mock.customerConversations(customer.id).length }}</strong>
              <span>咨询次数</span>
            </div>
          </div>
        </div>

        <div class="context-card">
          <div class="context-card__head">
            <h3>
              <el-icon><Box /></el-icon>
              最近订单
            </h3>
            <button class="context-link" type="button" @click="openAllOrders">
              全部
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-if="recentOrders.length" class="context-list">
            <button
              v-for="order in recentOrders"
              :key="order.id"
              class="context-row"
              type="button"
              @click="ui.openOrderDrawer(order.id)"
            >
              <span class="context-row__icon is-order">
                <el-icon><Box /></el-icon>
              </span>
              <span class="context-row__copy">
                <span class="context-row__title">{{ order.productName }}</span>
                <span>{{ order.orderNo }}</span>
              </span>
              <span class="context-row__end">
                <strong>{{ formatAmount(order.amount) }}</strong>
                <StatusTag kind="order" :value="order.orderStatus" />
              </span>
            </button>
          </div>
          <EmptyState
            v-else
            compact
            title="暂无订单"
            description="该客户还没有订单记录。"
          />
        </div>

        <div class="context-card">
          <div class="context-card__head">
            <h3>
              <el-icon><Tickets /></el-icon>
              相关工单
            </h3>
            <button class="context-link" type="button" @click="openAllTickets">
              全部
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-if="recentTickets.length" class="context-list">
            <button
              v-for="ticket in recentTickets"
              :key="ticket.id"
              class="context-row"
              type="button"
              @click="ui.openTicketDrawer(ticket.id)"
            >
              <span class="context-row__icon is-ticket">
                <el-icon><Tickets /></el-icon>
              </span>
              <span class="context-row__copy">
                <span class="context-row__title">{{ ticketTypeLabel(ticket.type) }}</span>
                <span>{{ ticket.ticketNo }}</span>
              </span>
              <span class="context-row__end">
                <StatusTag kind="priority" :value="ticket.priority" />
                <StatusTag kind="ticket" :value="ticket.status" />
              </span>
            </button>
          </div>
          <EmptyState
            v-else
            compact
            title="暂无工单"
            description="可从会话或订单创建售后工单。"
          />
          <button class="create-ticket-cta" type="button" @click="createTicket">
            <el-icon><Plus /></el-icon>
            创建售后工单
          </button>
        </div>

        <div class="context-note">
          <el-icon><ChatDotRound /></el-icon>
          <span>会话、订单与工单已建立关联，点击卡片即可查看完整信息。</span>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.workbench-page {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
  min-height: 0;
}

.workbench-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex: 0 0 auto;
}

.workbench-title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 7px;
  border: 1px solid #d8f5e9;
  border-radius: 5px;
  color: #0e9569;
  background: #f4fcf8;
  font-size: 9px;
  font-weight: 500;
}

.live-badge i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #0eaf78;
  animation: live-pulse 1.8s ease-in-out infinite;
}

.workbench-head__summary {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 9px 16px;
  border: 1px solid rgba(228, 228, 235, 0.8);
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.72);
}

.workbench-head__summary div {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.workbench-head__summary span {
  color: #96969f;
  font-size: 10px;
}

.workbench-head__summary strong {
  color: #424249;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
  font-weight: 700;
}

.workbench-grid {
  display: grid;
  grid-template-columns: 286px minmax(0, 1fr) 304px;
  gap: 14px;
  flex: 1;
  min-height: 0;
}

.panel-surface {
  border: 1px solid rgba(228, 228, 235, 0.82);
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 30px rgba(27, 29, 35, 0.045);
}

.queue-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.queue-tabs {
  display: flex;
  gap: 3px;
  flex: 0 0 auto;
  padding: 10px 10px 9px;
  border-bottom: 1px solid #f2f2f5;
}

.queue-tabs button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1;
  height: 31px;
  padding: 0 4px;
  border-radius: 7px;
  color: #93939d;
  background: transparent;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition:
    color 0.18s ease,
    background 0.18s ease;
}

.queue-tabs button:hover {
  color: #55555e;
  background: #f8f8fa;
}

.queue-tabs button.is-active {
  color: var(--admin-brand);
  background: #fff1ef;
  font-weight: 600;
}

.queue-tabs em {
  display: grid;
  place-items: center;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 4px;
  background: rgba(122, 122, 133, 0.1);
  font-size: 9px;
  font-style: normal;
  font-weight: 600;
}

.queue-tabs button.is-active em {
  color: var(--admin-brand);
  background: rgba(225, 37, 27, 0.09);
}

.queue-search {
  flex: 0 0 auto;
  padding: 0 10px 10px;
}

.queue-search :deep(.el-input__wrapper) {
  border-radius: 7px;
  background: #f8f8fa;
  box-shadow: none;
}

.queue-search :deep(.el-input__inner) {
  font-size: 11px;
}

.queue-list {
  flex: 1;
  min-height: 0;
  padding: 0 7px 10px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  width: 100%;
  margin-bottom: 4px;
  padding: 11px 8px;
  border: 1px solid transparent;
  border-radius: 10px;
  text-align: left;
  background: transparent;
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    background 0.18s ease;
}

.queue-item:hover {
  background: #fbfafb;
}

.queue-item.is-active {
  border-color: #ffdcd6;
  background: linear-gradient(135deg, #fff8f6, #fff1ee);
  box-shadow: inset 2px 0 0 var(--admin-brand);
}

.queue-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 33px;
  width: 33px;
  height: 33px;
  margin-top: 1px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(150deg, #8ea6df, #607dc0);
  font-size: 11px;
  font-weight: 700;
}

.queue-item.is-waiting .queue-avatar {
  background: linear-gradient(150deg, #ffab62, #ec6c27);
}

.queue-avatar i {
  position: absolute;
  right: -1px;
  top: -1px;
  width: 8px;
  height: 8px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #f0a000;
}

.queue-body {
  display: block;
  min-width: 0;
  flex: 1;
}

.queue-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.queue-topline strong {
  overflow: hidden;
  color: #45454c;
  font-size: 12px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.queue-topline time {
  flex: 0 0 auto;
  color: #b3b3bb;
  font-size: 9px;
}

.queue-title {
  display: block;
  margin-top: 3px;
  overflow: hidden;
  color: #7c7c86;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.queue-preview {
  display: block;
  margin-top: 4px;
  overflow: hidden;
  color: #a5a5ad;
  font-size: 10px;
  line-height: 1.5;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.queue-footline {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 7px;
}

.queue-footline :deep(.status-tag) {
  height: 18px;
  padding: 0 5px;
  font-size: 9px;
}

.queue-footline em {
  overflow: hidden;
  color: #b2b2ba;
  font-size: 9px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.waiting-pulse {
  width: 4px;
  height: 4px;
  margin-left: auto;
  border-radius: 50%;
  background: #ec9f00;
  animation: live-pulse 1.2s infinite ease-in-out;
}

.conversation-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.conversation-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  min-height: 69px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f1f4;
  background: linear-gradient(180deg, #fffdfc, #fff);
}

.conversation-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 37px;
  width: 37px;
  height: 37px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(150deg, #ff8b66, #d73423);
  font-size: 13px;
  font-weight: 700;
}

.conversation-avatar i {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 9px;
  height: 9px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #11b67a;
}

.conversation-head__copy {
  min-width: 0;
  flex: 1;
}

.conversation-head__title {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
}

.conversation-head__title h2 {
  overflow: hidden;
  color: #333339;
  font-size: 14px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-head__copy > p {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 5px;
  overflow: hidden;
  color: #a3a3ac;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-head__copy > p span {
  color: #d1d1d7;
}

.waiting-timer {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: #cc8300;
  font-size: 10px;
}

.conversation-actions {
  display: flex;
  align-items: center;
  gap: 7px;
  flex: 0 0 auto;
}

.conversation-actions :deep(.el-button) {
  height: 31px;
  padding: 0 11px;
  border-radius: 7px;
  font-size: 11px;
}

.conversation-close {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 5px 2px;
  color: #a0a0aa;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.conversation-close:hover {
  color: var(--admin-brand);
}

.awaiting-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  margin: 10px 13px 0;
  padding: 9px 11px;
  border: 1px solid #ffe4c1;
  border-radius: 9px;
  background: #fffaf0;
}

.awaiting-banner__icon {
  display: grid;
  place-items: center;
  flex: 0 0 27px;
  width: 27px;
  height: 27px;
  border-radius: 8px;
  color: #d38a00;
  background: #fff0d3;
  font-size: 14px;
}

.awaiting-banner > div {
  flex: 1;
  min-width: 0;
}

.awaiting-banner strong {
  color: #8b620f;
  font-size: 11px;
  font-weight: 600;
}

.awaiting-banner p {
  margin-top: 2px;
  color: #b38a44;
  font-size: 10px;
}

.awaiting-banner :deep(.el-button) {
  flex: 0 0 auto;
  height: 27px;
  font-size: 10px;
}

.closed-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  margin: 10px 13px 0;
  padding: 8px 10px;
  border-radius: 8px;
  color: #898992;
  background: #f7f7f9;
  font-size: 10px;
}

.conversation-footnote {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex: 0 0 auto;
  padding: 12px 16px;
  border-top: 1px solid #f1f1f4;
  color: #9b9ba5;
  background: #fbfbfc;
  font-size: 11px;
}

.conversation-footnote.is-closed {
  justify-content: flex-start;
  gap: 5px;
}

.conversation-footnote :deep(.el-button) {
  height: 28px;
  font-size: 10px;
}

.context-panel {
  display: flex;
  flex-direction: column;
  gap: 11px;
  min-height: 0;
  padding-bottom: 4px;
  overflow-y: auto;
}

.context-card {
  flex: 0 0 auto;
  padding: 14px;
  border: 1px solid rgba(228, 228, 235, 0.82);
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 6px 20px rgba(27, 29, 35, 0.035);
}

.customer-card {
  padding: 0;
  overflow: hidden;
}

.customer-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 14px 11px;
  background:
    radial-gradient(circle at 92% 10%, rgba(255, 117, 74, 0.15), transparent 36%),
    linear-gradient(135deg, #fffaf5, #fff);
}

.customer-card__avatar {
  display: grid;
  place-items: center;
  flex: 0 0 39px;
  width: 39px;
  height: 39px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(145deg, #ff9a6b, #d93b25);
  font-size: 14px;
  font-weight: 700;
}

.customer-card__name {
  display: flex;
  align-items: center;
  gap: 6px;
}

.customer-card__name h3 {
  color: #3d3d43;
  font-size: 14px;
  font-weight: 650;
}

.demo-label {
  padding: 2px 5px;
  border: 1px solid #ffe0d4;
  border-radius: 4px;
  color: #e46a3e;
  background: #fff8f4;
  font-size: 9px;
}

.customer-card__head p {
  margin-top: 4px;
  color: #a6a6ae;
  font-size: 10px;
  letter-spacing: 0.02em;
}

.customer-card__meta {
  display: flex;
  flex-direction: column;
  gap: 7px;
  padding: 0 14px 12px;
}

.customer-card__meta span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #8d8d96;
  font-size: 10px;
}

.customer-card__meta :deep(.el-icon) {
  color: #b8b8c0;
  font-size: 11px;
}

.customer-card__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid #f2f2f5;
}

.customer-card__stats div {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 10px 0;
  border-right: 1px solid #f2f2f5;
}

.customer-card__stats div:last-child {
  border-right: 0;
}

.customer-card__stats strong {
  color: #48484f;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 16px;
  font-weight: 700;
}

.customer-card__stats span {
  color: #a6a6ae;
  font-size: 9px;
}

.context-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 9px;
}

.context-card__head h3 {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #5b5b63;
  font-size: 11px;
  font-weight: 650;
}

.context-card__head h3 :deep(.el-icon) {
  color: #a3a3ac;
  font-size: 12px;
}

.context-link {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  padding: 0;
  color: #aaaab2;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.context-link:hover {
  color: var(--admin-brand);
}

.context-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.context-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px;
  border: 1px solid transparent;
  border-radius: 8px;
  text-align: left;
  background: transparent;
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    background 0.18s ease;
}

.context-row:hover {
  border-color: #f4e3dd;
  background: #fffaf8;
}

.context-row__icon {
  display: grid;
  place-items: center;
  flex: 0 0 27px;
  width: 27px;
  height: 27px;
  border-radius: 7px;
  font-size: 12px;
}

.context-row__icon.is-order {
  color: #e36832;
  background: #fff4ed;
}

.context-row__icon.is-ticket {
  color: #d63b2c;
  background: #fff0ee;
}

.context-row__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.context-row__title {
  overflow: hidden;
  color: #57575f;
  font-size: 11px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-row__copy > span:last-child {
  color: #aaaab2;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 9px;
}

.context-row__end {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  flex: 0 0 auto;
}

.context-row__end strong {
  color: #d13e2d;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
}

.context-row__end :deep(.status-tag) {
  height: 17px;
  padding: 0 5px;
  font-size: 9px;
}

.create-ticket-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  height: 32px;
  margin-top: 10px;
  border: 1px dashed #ead8d3;
  border-radius: 8px;
  color: #b46c54;
  background: #fffaf8;
  font-size: 10px;
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    color 0.18s ease;
}

.create-ticket-cta:hover {
  border-color: #e2b49f;
  color: var(--admin-brand);
}

.context-note {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 0 5px;
  color: #a6a6af;
  font-size: 8px;
  line-height: 1.6;
}

.context-note :deep(.el-icon) {
  flex: 0 0 auto;
  margin-top: 1px;
  font-size: 10px;
}

@keyframes live-pulse {
  0%,
  100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

@media (max-width: 1340px) {
  .workbench-grid {
    grid-template-columns: 266px minmax(0, 1fr) 282px;
  }

  .context-card {
    padding: 12px;
  }
}

@media (max-width: 1180px) {
  .workbench-grid {
    grid-template-columns: 264px minmax(0, 1fr);
  }

  .context-panel {
    display: none;
  }

  .conversation-actions :deep(.el-button:nth-child(2)) {
    display: none;
  }
}

@media (max-width: 900px) {
  .workbench-head__summary {
    display: none;
  }

  .workbench-grid {
    grid-template-columns: 224px minmax(0, 1fr);
  }

  .queue-tabs {
    padding: 8px 6px;
  }

  .queue-tabs button {
    font-size: 9px;
  }

  .conversation-head__copy > p {
    display: none;
  }

  .conversation-actions :deep(.el-button) {
    display: none;
  }

  .awaiting-banner p {
    display: none;
  }
}
</style>
