<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChatDotRound,
  Headset,
  Search,
  ShoppingBag,
} from '@element-plus/icons-vue'
import type {
  ConversationDetail,
  ConversationSummary,
  Page,
} from '@/types/api'
import { buyerApi } from '@/api/buyer'
import { showError } from '@/api/http'
import { fromNow } from '@/utils/format'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'

const route = useRoute()
const router = useRouter()

const result = ref<Page<ConversationSummary>>({
  items: [],
  total: 0,
  page: 1,
  page_size: 30,
  counts: {},
})
const selectedId = ref<number | null>(null)
const detail = ref<ConversationDetail | null>(null)
const keyword = ref('')
const draft = ref('')
const loadingList = ref(true)
const loadingDetail = ref(false)
const sending = ref(false)
let listTimer: number | null = null
let detailTimer: number | null = null

const conversations = computed(() => result.value.items)
const selectedConversation = computed(
  () => conversations.value.find((item) => item.id === selectedId.value) || detail.value?.conversation || null,
)
const messages = computed(() => detail.value?.messages || [])
const isClosed = computed(() => selectedConversation.value?.status === 'closed')
const canSend = computed(() => Boolean(selectedConversation.value) && !isClosed.value)

function pickInitialConversation(): void {
  const requested = Number(route.query.conversation)
  const fromQuery = conversations.value.find((item) => item.id === requested)
  const next = fromQuery || conversations.value[0]
  if (next) {
    void selectConversation(next.id, !fromQuery)
  } else {
    selectedId.value = null
    detail.value = null
  }
}

async function loadConversations(silent = false): Promise<void> {
  if (!silent) loadingList.value = true
  try {
    result.value = await buyerApi.getConversations({
      keyword: keyword.value.trim() || undefined,
      page: 1,
      page_size: 30,
    })
    if (selectedId.value && !conversations.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = null
      detail.value = null
      pickInitialConversation()
    }
  } catch (error) {
    if (!silent) showError(error)
  } finally {
    loadingList.value = false
  }
}

async function loadDetail(silent = false): Promise<void> {
  if (!selectedId.value) return
  if (!silent) loadingDetail.value = true
  try {
    detail.value = await buyerApi.getConversation(selectedId.value)
  } catch (error) {
    if (!silent) showError(error)
  } finally {
    loadingDetail.value = false
  }
}

async function selectConversation(id: number, updateQuery = true): Promise<void> {
  if (selectedId.value === id && detail.value) return
  selectedId.value = id
  detail.value = null
  if (updateQuery && String(route.query.conversation) !== String(id)) {
    await router.replace({
      path: '/consumer/chat',
      query: { conversation: String(id) },
    })
  }
  await loadDetail()
}

function startPolling(): void {
  listTimer = window.setInterval(() => {
    void loadConversations(true)
  }, 5000)
  detailTimer = window.setInterval(() => {
    void loadDetail(true)
  }, 2000)
}

function search(): void {
  selectedId.value = null
  detail.value = null
  void loadConversations().then(() => pickInitialConversation())
}

async function sendMessage(): Promise<void> {
  const content = draft.value.trim()
  if (!content || !selectedConversation.value || !canSend.value || sending.value) return
  sending.value = true
  try {
    await buyerApi.sendMessage(selectedConversation.value.id, content)
    draft.value = ''
    await loadDetail(true)
    await nextTick()
  } catch (error) {
    showError(error)
  } finally {
    sending.value = false
  }
}

watch(
  () => route.query.conversation,
  (value) => {
    const id = Number(value)
    if (Number.isFinite(id) && id !== selectedId.value) {
      void selectConversation(id, false)
    }
  },
)

onMounted(async () => {
  await loadConversations()
  pickInitialConversation()
  startPolling()
})

onBeforeUnmount(() => {
  if (listTimer) window.clearInterval(listTimer)
  if (detailTimer) window.clearInterval(detailTimer)
})
</script>

<template>
  <div class="buyer-chat-page">
    <aside v-loading="loadingList" class="conversation-list-panel">
      <div class="list-head">
        <div>
          <p class="eyebrow">HUMAN SERVICE</p>
          <h1>人工会话</h1>
        </div>
        <span class="list-count">{{ result.total }}</span>
      </div>
      <p class="list-note">转人工后才会创建会话，AI 阶段不开放聊天。</p>

      <div class="list-search">
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          size="small"
          placeholder="搜索会话或订单号"
          clearable
          @keyup.enter="search"
          @clear="search"
        />
      </div>

      <div class="conversation-list">
        <button
          v-for="conversation in conversations"
          :key="conversation.id"
          type="button"
          class="conversation-item"
          :class="{ 'is-active': conversation.id === selectedId }"
          @click="selectConversation(conversation.id)"
        >
          <span class="conversation-avatar">
            <el-icon><Headset /></el-icon>
            <i v-if="conversation.status === 'human'" />
          </span>
          <span class="conversation-copy">
            <span class="conversation-top">
              <strong>{{ conversation.order_product || '售后人工会话' }}</strong>
              <time>{{ fromNow(conversation.updated_at) }}</time>
            </span>
            <span class="conversation-preview">
              {{ conversation.last_message || '暂无消息' }}
            </span>
            <span class="conversation-meta">
              <StatusTag kind="conversation" :value="conversation.status" />
              <em v-if="conversation.merchant_name">
                <el-icon><ShoppingBag /></el-icon>
                {{ conversation.merchant_name }}
              </em>
            </span>
          </span>
        </button>

        <EmptyState
          v-if="!loadingList && conversations.length === 0"
          compact
          title="暂无人工会话"
          description="在售后详情中提交「不满意，转人工」后，这里会开放与平台客服的对话框。"
        >
          <el-button type="primary" @click="router.push('/consumer/after-sales')">
            查看售后服务
          </el-button>
        </EmptyState>
      </div>
    </aside>

    <section class="conversation-panel">
      <template v-if="selectedConversation">
        <header class="conversation-head">
          <span class="conversation-head__icon"><el-icon><Headset /></el-icon></span>
          <div class="conversation-head__copy">
            <div>
              <h2>平台人工客服</h2>
              <StatusTag kind="conversation" :value="selectedConversation.status" dot />
              <span v-if="selectedConversation.merchant_name" class="merchant-chip">
                <el-icon><ShoppingBag /></el-icon>
                {{ selectedConversation.merchant_name }} 已加入
              </span>
            </div>
            <p>
              {{ selectedConversation.assigned_agent_name || '等待平台客服接入' }}
              <span>·</span>
              {{ selectedConversation.order_no || '关联售后会话' }}
              <span>·</span>
              会话 #{{ selectedConversation.id }}
            </p>
          </div>
          <span class="conversation-head__sync"><i /> 自动刷新</span>
        </header>

        <div v-if="selectedConversation.status === 'waiting'" class="waiting-banner">
          <span class="waiting-banner__dot" />
          <span>已进入人工队列，平台客服接入后会自动提醒，您可以先留言。</span>
        </div>
        <div v-if="isClosed" class="closed-banner">
          本次人工会话已结束，如需继续咨询请针对订单重新提交售后。
        </div>

        <ChatStream
          :key="selectedConversation.id"
          :messages="messages"
          current-role="consumer"
          empty-title="等待客服查看消息"
          empty-description="您可以先描述问题，人工客服接入后会看到完整记录。"
        />

        <ChatComposer
          v-if="!isClosed"
          v-model="draft"
          :disabled="sending"
          :loading="sending"
          :placeholder="selectedConversation.status === 'waiting' ? '客服接入前，您可以先留言…' : '回复平台客服…'"
          @send="sendMessage"
        />
        <div v-else class="closed-foot">
          <span>会话已结束</span>
          <button type="button" @click="router.push('/consumer/after-sales')">
            查看售后服务
          </button>
        </div>
      </template>

      <EmptyState
        v-else-if="!loadingList"
        title="暂无进行中的人工会话"
        description="只有转人工后才会开放对话框。AI 处理阶段请查看售后详情。"
      >
        <el-button type="primary" @click="router.push('/consumer/after-sales')">
          查看售后服务
        </el-button>
      </EmptyState>

      <div v-else class="chat-loading">
        <el-icon><ChatDotRound /></el-icon>
        <span>正在加载会话…</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.buyer-chat-page {
  display: grid;
  grid-template-columns: 315px minmax(0, 1fr);
  gap: 14px;
  height: calc(100vh - 64px - 56px);
  min-height: 540px;
}

.conversation-list-panel,
.conversation-panel {
  min-height: 0;
  overflow: hidden;
  border: 1px solid #ececf1;
  border-radius: 15px;
  background: #fff;
  box-shadow: 0 8px 25px rgba(28, 29, 35, 0.04);
}

.conversation-list-panel {
  display: flex;
  flex-direction: column;
  padding: 17px 12px 10px;
}

.list-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 1px 6px 7px;
}

.list-head h1 {
  margin-top: 3px;
  color: #2e2e34;
  font-size: 20px;
  font-weight: 750;
  letter-spacing: -0.02em;
}

.list-count {
  display: grid;
  place-items: center;
  min-width: 22px;
  height: 22px;
  border-radius: 7px;
  color: #a1a1a9;
  background: #f5f5f8;
  font-size: 10px;
}

.list-note {
  padding: 0 6px 9px;
  color: #a3a3ab;
  font-size: 9px;
  line-height: 1.65;
}

.list-search {
  padding: 0 3px 9px;
}

.list-search :deep(.el-input__wrapper) {
  border-radius: 7px;
  background: #fafafb;
  box-shadow: 0 0 0 1px #ececf1 inset;
}

.list-search :deep(.el-input__inner) {
  font-size: 10px;
}

.conversation-list {
  flex: 1;
  min-height: 0;
  padding: 1px;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  width: 100%;
  margin-bottom: 4px;
  padding: 10px 8px;
  border: 1px solid transparent;
  border-radius: 10px;
  text-align: left;
  background: transparent;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.conversation-item:hover {
  background: #fbfaf9;
}

.conversation-item.is-active {
  border-color: #ffddcb;
  background: linear-gradient(135deg, #fffaf6, #fff2e9);
  box-shadow: inset 2px 0 0 #ff5b0d;
}

.conversation-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 33px;
  width: 33px;
  height: 33px;
  margin-top: 1px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(145deg, #ff9565, #e6521c);
  font-size: 15px;
}

.conversation-avatar i {
  position: absolute;
  right: -1px;
  top: -1px;
  width: 8px;
  height: 8px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #15b97d;
}

.conversation-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.conversation-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.conversation-top strong {
  overflow: hidden;
  color: #4a4a51;
  font-size: 11px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-top time {
  flex: 0 0 auto;
  color: #b2b2ba;
  font-size: 8px;
}

.conversation-preview {
  overflow: hidden;
  color: #9c9ca5;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 0;
}

.conversation-meta :deep(.status-tag) {
  height: 18px;
  padding: 0 5px;
  font-size: 8px;
}

.conversation-meta em {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  overflow: hidden;
  color: #107c7c;
  font-size: 8px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-panel {
  display: flex;
  flex-direction: column;
}

.conversation-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  min-height: 64px;
  padding: 11px 17px;
  border-bottom: 1px solid #f1f1f4;
  background: linear-gradient(180deg, #fffdfb, #fff);
}

.conversation-head__icon {
  display: grid;
  place-items: center;
  flex: 0 0 37px;
  width: 37px;
  height: 37px;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #ff9c63, #ea5520);
  font-size: 18px;
}

.conversation-head__copy {
  min-width: 0;
  flex: 1;
}

.conversation-head__copy > div {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
}

.conversation-head__copy h2 {
  color: #3e3e45;
  font-size: 13px;
  font-weight: 650;
}

.conversation-head__copy p {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 4px;
  color: #a3a3ab;
  font-size: 9px;
}

.conversation-head__copy p span {
  color: #d4d4da;
}

.merchant-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  border-radius: 4px;
  color: #0e7d7d;
  background: #eaf8f7;
  font-size: 8px;
}

.conversation-head__sync {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #b2b2ba;
  font-size: 8px;
}

.conversation-head__sync i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #15b97d;
}

.waiting-banner,
.closed-banner {
  display: flex;
  align-items: center;
  gap: 7px;
  flex: 0 0 auto;
  padding: 8px 17px;
  border-bottom: 1px solid #fff0d7;
  color: #ab740f;
  background: #fffaf0;
  font-size: 10px;
}

.waiting-banner__dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #eca100;
  animation: waiting-pulse 1.5s infinite;
}

.closed-banner {
  border-bottom-color: #efeff3;
  color: #8d8d96;
  background: #fafafb;
}

.closed-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex: 0 0 auto;
  padding: 12px 17px;
  border-top: 1px solid #f1f1f4;
  color: #a0a0a8;
  background: #fbfbfc;
  font-size: 10px;
}

.closed-foot button {
  padding: 0;
  color: #e85c1a;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.chat-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  flex: 1;
  color: #a3a3ab;
  font-size: 10px;
}

@keyframes waiting-pulse {
  0%,
  100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

@media (max-width: 800px) {
  .buyer-chat-page {
    display: flex;
    flex-direction: column;
    height: auto;
    min-height: 0;
  }

  .conversation-list-panel {
    flex: 0 0 auto;
    max-height: 245px;
  }

  .conversation-panel {
    min-height: 540px;
    height: calc(100dvh - 300px);
  }

  .conversation-head__copy p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .conversation-head__sync {
    display: none;
  }
}
</style>
