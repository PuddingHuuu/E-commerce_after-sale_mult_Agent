<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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
import { merchantApi } from '@/api/merchant'
import { showError } from '@/api/http'
import { fromNow } from '@/utils/format'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'

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
  () => detail.value?.conversation || conversations.value.find((item) => item.id === selectedId.value) || null,
)
const messages = computed(() => detail.value?.messages || [])
const canReply = computed(() => selectedConversation.value?.status === 'human')
const isClosed = computed(() => selectedConversation.value?.status === 'closed')

async function loadConversations(silent = false): Promise<void> {
  if (!silent) loadingList.value = true
  try {
    result.value = await merchantApi.getConversations({
      keyword: keyword.value.trim() || undefined,
      page: 1,
      page_size: 30,
    })
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
    detail.value = await merchantApi.getConversation(selectedId.value)
  } catch (error) {
    if (!silent) showError(error)
  } finally {
    loadingDetail.value = false
  }
}

async function selectConversation(id: number): Promise<void> {
  if (selectedId.value === id && detail.value) return
  selectedId.value = id
  detail.value = null
  draft.value = ''
  await loadDetail()
}

function pickInitialConversation(): void {
  if (selectedId.value && conversations.value.some((item) => item.id === selectedId.value)) {
    void loadDetail(true)
    return
  }
  const next = conversations.value[0]
  if (next) {
    void selectConversation(next.id)
  } else {
    selectedId.value = null
    detail.value = null
  }
}

async function search(): Promise<void> {
  selectedId.value = null
  detail.value = null
  await loadConversations()
  pickInitialConversation()
}

async function sendMessage(): Promise<void> {
  const content = draft.value.trim()
  if (!content || !selectedConversation.value || !canReply.value || sending.value) return
  sending.value = true
  try {
    await merchantApi.sendMessage(selectedConversation.value.id, content)
    draft.value = ''
    await loadDetail(true)
    await loadConversations(true)
    await nextTick()
  } catch (error) {
    showError(error)
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  await loadConversations()
  pickInitialConversation()
  listTimer = window.setInterval(() => void loadConversations(true), 5000)
  detailTimer = window.setInterval(() => void loadDetail(true), 2000)
})

onBeforeUnmount(() => {
  if (listTimer) window.clearInterval(listTimer)
  if (detailTimer) window.clearInterval(detailTimer)
})
</script>

<template>
  <div class="merchant-page">
    <header class="merchant-page-head">
      <div>
        <p class="eyebrow">MERCHANT COLLABORATION</p>
        <h1>协同会话</h1>
        <p>平台客服邀请您加入的售后会话会出现在这里。您只能参与会话，无法查看工单或平台订单。</p>
      </div>
      <div class="merchant-badge">
        <span><el-icon><ShoppingBag /></el-icon></span>
        <div>
          <strong>{{ result.total }}</strong>
          <small>个受邀会话</small>
        </div>
      </div>
    </header>

    <div class="merchant-workspace">
      <aside class="merchant-list-panel">
        <div class="list-head">
          <h2>会话列表</h2>
          <span>{{ result.total }}</span>
        </div>
        <div class="list-search">
          <el-input
            v-model="keyword"
            :prefix-icon="Search"
            placeholder="搜索消费者或消息"
            clearable
            @keyup.enter="search"
            @clear="search"
          />
        </div>

        <div v-loading="loadingList" class="merchant-conversations">
          <button
            v-for="conversation in conversations"
            :key="conversation.id"
            type="button"
            class="merchant-conversation-item"
            :class="{ 'is-active': selectedId === conversation.id }"
            @click="selectConversation(conversation.id)"
          >
            <span class="merchant-avatar">
              {{ conversation.customer_name.slice(0, 1) }}
              <i v-if="conversation.status === 'human'" />
            </span>
            <span class="merchant-conversation-copy">
              <span class="conversation-top">
                <strong>{{ conversation.customer_name }}</strong>
                <time>{{ fromNow(conversation.updated_at) }}</time>
              </span>
              <span class="conversation-preview">
                {{ conversation.last_message || '暂无消息' }}
              </span>
              <span class="conversation-foot">
                <StatusTag kind="conversation" :value="conversation.status" />
                <em>平台：{{ conversation.assigned_agent_name || '待接入' }}</em>
              </span>
            </span>
          </button>

          <EmptyState
            v-if="!loadingList && conversations.length === 0"
            compact
            title="暂无受邀会话"
            description="当平台客服邀请您参与售后沟通时，会话会自动出现在这里。"
          />
        </div>
      </aside>

      <section class="merchant-chat-panel">
        <template v-if="selectedConversation">
          <header class="merchant-chat-head">
            <span class="chat-avatar">{{ selectedConversation.customer_name.slice(0, 1) }}</span>
            <div>
              <div>
                <h2>{{ selectedConversation.customer_name }}</h2>
                <StatusTag kind="conversation" :value="selectedConversation.status" dot />
              </div>
              <p>
                商家协同会话
                <span>·</span>
                平台客服：{{ selectedConversation.assigned_agent_name || '待接入' }}
                <span>·</span>
                会话 #{{ selectedConversation.id }}
              </p>
            </div>
            <span class="chat-sync"><i /> 自动刷新</span>
          </header>

          <div v-if="selectedConversation.status === 'waiting'" class="merchant-banner is-waiting">
            <span><el-icon><Headset /></el-icon></span>
            <p>平台客服尚未接入会话。您可以在平台客服接入后参与沟通。</p>
          </div>
          <div v-if="isClosed" class="merchant-banner is-closed">
            <el-icon><ChatDotRound /></el-icon>
            <p>本次协同会话已结束，仅支持查看历史消息。</p>
          </div>

          <ChatStream
            :key="selectedConversation.id"
            :messages="messages"
            current-role="merchant"
            empty-title="暂无消息"
            empty-description="消费者与平台客服的沟通记录会显示在这里。"
          />

          <ChatComposer
            v-if="canReply"
            v-model="draft"
            :disabled="sending"
            :loading="sending"
            placeholder="以商家客服身份回复…"
            @send="sendMessage"
          />
          <div v-else-if="selectedConversation.status === 'waiting'" class="merchant-chat-foot">
            <span>等待平台客服接入后即可回复</span>
          </div>
          <div v-else class="merchant-chat-foot is-closed">
            <span>会话已结束，无法继续发送消息</span>
          </div>
        </template>

        <EmptyState
          v-else
          title="选择一个受邀会话"
          description="平台客服邀请您加入会话后，可以从左侧进入并参与沟通。"
        />
      </section>
    </div>
  </div>
</template>

<style scoped>
.merchant-page {
  height: 100%;
}

.merchant-page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.merchant-page-head h1 {
  margin-top: 4px;
  color: #2f3d34;
  font-size: 27px;
  font-weight: 750;
  letter-spacing: -0.03em;
}

.merchant-page-head p:last-child {
  margin-top: 8px;
  color: #8b9c90;
  font-size: 14px;
}

.merchant-badge {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 12px;
  border: 1px solid #dce7df;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
}

.merchant-badge > span {
  display: grid;
  place-items: center;
  width: 29px;
  height: 29px;
  border-radius: 8px;
  color: #66816d;
  background: #eef5ef;
  font-size: 14px;
}

.merchant-badge > div {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.merchant-badge strong {
  color: #3f5147;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
  line-height: 1;
}

.merchant-badge small {
  color: #8b9c90;
  font-size: 11px;
}

.merchant-workspace {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 13px;
  height: calc(100vh - 68px - 112px);
  min-height: 560px;
}

.merchant-list-panel,
.merchant-chat-panel {
  min-height: 0;
  overflow: hidden;
  border: 1px solid #dce7df;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 26px rgba(92, 116, 99, 0.05);
}

.merchant-list-panel {
  display: flex;
  flex-direction: column;
  padding: 14px 10px 9px;
}

.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px 9px;
}

.list-head h2 {
  color: #3f5147;
  font-size: 14px;
  font-weight: 650;
}

.list-head span {
  display: grid;
  place-items: center;
  min-width: 24px;
  height: 24px;
  border-radius: 7px;
  color: #8b9c90;
  background: #f1f6f2;
  font-size: 12px;
}

.list-search {
  padding: 0 2px 8px;
}

.list-search :deep(.el-input__wrapper) {
  height: 34px;
  border-radius: 8px;
  background: #f7faf7;
  box-shadow: 0 0 0 1px #e0e9e2 inset;
}

.list-search :deep(.el-input__inner) {
  font-size: 13px;
}

.merchant-conversations {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.merchant-conversation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  margin-bottom: 3px;
  padding: 11px 9px;
  border: 1px solid transparent;
  border-radius: 10px;
  text-align: left;
  background: transparent;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.merchant-conversation-item:hover {
  background: #f7faf7;
}

.merchant-conversation-item.is-active {
  border-color: #d5e5d9;
  background: linear-gradient(135deg, #f7fbf8, #eff6f1);
  box-shadow: inset 2px 0 0 #7d9b84;
}

.merchant-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 35px;
  width: 35px;
  height: 35px;
  margin-top: 1px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #8a9fd5, #6075b3);
  font-size: 12px;
  font-weight: 600;
}

.merchant-avatar i {
  position: absolute;
  top: -1px;
  right: -1px;
  width: 7px;
  height: 7px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #14b87b;
}

.merchant-conversation-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.conversation-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
}

.conversation-top strong {
  color: #45564a;
  font-size: 13px;
  font-weight: 600;
}

.conversation-top time {
  flex: 0 0 auto;
  color: #a3aea6;
  font-size: 11px;
}

.conversation-preview {
  overflow: hidden;
  color: #93a096;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-foot {
  display: flex;
  align-items: center;
  gap: 5px;
}

.conversation-foot :deep(.status-tag) {
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
}

.conversation-foot em {
  overflow: hidden;
  color: #9aa79d;
  font-size: 11px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-chat-panel {
  display: flex;
  flex-direction: column;
  --chat-accent: #7d9b84;
  --chat-accent-deep: #67826e;
}

.merchant-chat-head {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 0 0 auto;
  min-height: 72px;
  padding: 12px 17px;
  border-bottom: 1px solid #edf4ee;
  background: linear-gradient(180deg, #fbfdfb, #fff);
}

.chat-avatar {
  display: grid;
  place-items: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(145deg, #8ba0d7, #6076b4);
  font-size: 13px;
  font-weight: 600;
}

.merchant-chat-head > div {
  min-width: 0;
  flex: 1;
}

.merchant-chat-head > div > div {
  display: flex;
  align-items: center;
  gap: 6px;
}

.merchant-chat-head h2 {
  color: #3f5147;
  font-size: 14px;
  font-weight: 650;
}

.merchant-chat-head p {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  overflow: hidden;
  color: #93a096;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-chat-head p span {
  color: #d6dfd8;
}

.chat-sync {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #9aa79d;
  font-size: 11px;
}

.chat-sync i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #15b87b;
}

.merchant-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  margin: 8px 12px 0;
  padding: 9px 11px;
  border-radius: 7px;
  font-size: 12px;
}

.merchant-banner.is-waiting {
  color: #987123;
  background: #fffaf0;
}

.merchant-banner.is-waiting > span {
  font-size: 13px;
}

.merchant-banner.is-closed {
  color: #8b968f;
  background: #f7faf8;
}

.merchant-chat-foot {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  padding: 12px 16px;
  border-top: 1px solid #edf4ee;
  color: #93a096;
  background: #fbfdfb;
  font-size: 12px;
}

.merchant-chat-foot.is-closed {
  justify-content: flex-start;
}

@media (max-width: 860px) {
  .merchant-page-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .merchant-page-head h1 {
    font-size: 23px;
  }

  .merchant-badge {
    display: none;
  }

  .merchant-workspace {
    display: flex;
    flex-direction: column;
    height: auto;
  }

  .merchant-list-panel {
    max-height: 235px;
  }

  .merchant-chat-panel {
    height: calc(100dvh - 250px);
    min-height: 500px;
  }

  .chat-sync {
    display: none;
  }
}
</style>
