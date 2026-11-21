<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowRight,
  ChatDotRound,
  CircleClose,
  Headset,
  Plus,
  Search,
  ShoppingBag,
  Tickets,
  User,
} from '@element-plus/icons-vue'
import type {
  ConversationDetail,
  ConversationSummary,
  MerchantOption,
  Page,
} from '@/types/api'
import { platformApi } from '@/api/platform'
import { showError } from '@/api/http'
import { fromNow } from '@/utils/format'
import { platformConversationFilters, ticketCategoryLabel } from '@/utils/labels'
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
const statusFilter = ref('')
const keyword = ref('')
const appliedKeyword = ref('')
const loadingList = ref(true)
const loadingDetail = ref(false)
const selectedId = ref<number | null>(null)
const detail = ref<ConversationDetail | null>(null)
const draft = ref('')
const sending = ref(false)
const accepting = ref(false)
let listTimer: number | null = null
let detailTimer: number | null = null

const inviteVisible = ref(false)
const merchantKeyword = ref('')
const merchantLoading = ref(false)
const merchants = ref<MerchantOption[]>([])
const selectedMerchantId = ref<number | null>(null)
const inviting = ref(false)

const conversations = computed(() => result.value.items)
const selectedConversation = computed<ConversationSummary | null>(
  () => detail.value?.conversation || conversations.value.find((item) => item.id === selectedId.value) || null,
)
const messages = computed(() => detail.value?.messages || [])
const linkedTickets = computed(() => detail.value?.linked_tickets || [])
const canReply = computed(() => selectedConversation.value?.status === 'human')
const isClosed = computed(() => selectedConversation.value?.status === 'closed')
const hasMerchant = computed(() => Boolean(selectedConversation.value?.merchant_id))

const filterTabs = computed(() =>
  platformConversationFilters.map((item) => ({
    ...item,
    count: item.key ? result.value.counts?.[item.key] ?? 0 : result.value.counts?.all ?? 0,
  })),
)

async function loadConversations(silent = false): Promise<void> {
  if (!silent) loadingList.value = true
  try {
    result.value = await platformApi.getConversations({
      status: statusFilter.value || undefined,
      keyword: appliedKeyword.value || undefined,
      page: 1,
      page_size: 30,
    })
    if (selectedId.value && !conversations.value.some((item) => item.id === selectedId.value)) {
      // Keep the selected conversation open if it moved out of the current filter.
      if (!detail.value) {
        selectedId.value = null
      }
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
    detail.value = await platformApi.getConversation(selectedId.value)
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
  draft.value = ''
  if (updateQuery && String(route.query.conversation) !== String(id)) {
    await router.replace({
      path: '/platform/conversations',
      query: { ...route.query, conversation: String(id) },
    })
  }
  await loadDetail()
}

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

function switchFilter(status: string): void {
  if (statusFilter.value === status) return
  statusFilter.value = status
  void loadConversations().then(pickInitialConversation)
}

function search(): void {
  appliedKeyword.value = keyword.value.trim()
  void loadConversations().then(pickInitialConversation)
}

async function acceptConversation(): Promise<void> {
  if (!selectedConversation.value || selectedConversation.value.status !== 'waiting') return
  accepting.value = true
  try {
    await platformApi.acceptConversation(selectedConversation.value.id)
    ElMessage.success('已接入会话，可以开始回复')
    await Promise.all([loadConversations(true), loadDetail(true)])
  } catch (error) {
    showError(error)
  } finally {
    accepting.value = false
  }
}

async function sendMessage(): Promise<void> {
  const content = draft.value.trim()
  if (!content || !selectedConversation.value || !canReply.value || sending.value) return
  sending.value = true
  try {
    await platformApi.sendMessage(selectedConversation.value.id, content)
    draft.value = ''
    await Promise.all([loadDetail(true), loadConversations(true)])
    await nextTick()
  } catch (error) {
    showError(error)
  } finally {
    sending.value = false
  }
}

async function closeConversation(): Promise<void> {
  if (!selectedConversation.value || isClosed.value) return
  try {
    await ElMessageBox.confirm(
      '结束会话后，消费者和商家都不能继续发送消息，关联工单将同步关闭。',
      '结束会话',
      {
        confirmButtonText: '结束会话',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'platform-message-box',
      },
    )
    await platformApi.closeConversation(selectedConversation.value.id)
    ElMessage.success('会话已结束')
    await Promise.all([loadConversations(true), loadDetail(true)])
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') showError(error)
  }
}

async function openInviteDialog(): Promise<void> {
  inviteVisible.value = true
  merchantKeyword.value = ''
  selectedMerchantId.value = null
  await searchMerchants()
}

async function searchMerchants(): Promise<void> {
  merchantLoading.value = true
  try {
    merchants.value = await platformApi.searchMerchants(merchantKeyword.value.trim())
  } catch (error) {
    showError(error)
  } finally {
    merchantLoading.value = false
  }
}

async function confirmInvite(): Promise<void> {
  if (!selectedConversation.value || !selectedMerchantId.value) {
    ElMessage.warning('请选择商家')
    return
  }
  inviting.value = true
  try {
    const result = await platformApi.inviteMerchant(
      selectedConversation.value.id,
      selectedMerchantId.value,
    )
    ElMessage.success(`已邀请「${result.merchant.store_name}」加入会话`)
    inviteVisible.value = false
    await Promise.all([loadDetail(true), loadConversations(true)])
  } catch (error) {
    showError(error)
  } finally {
    inviting.value = false
  }
}

function openTicket(ticketId: number): void {
  router.push({ path: '/platform/tickets', query: { ticket: String(ticketId) } })
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
  listTimer = window.setInterval(() => void loadConversations(true), 5000)
  detailTimer = window.setInterval(() => void loadDetail(true), 2000)
})

onBeforeUnmount(() => {
  if (listTimer) window.clearInterval(listTimer)
  if (detailTimer) window.clearInterval(detailTimer)
})
</script>

<template>
  <div class="platform-conversations-page">
    <header class="page-head conversations-head">
      <div>
        <p class="eyebrow">HUMAN CONVERSATIONS</p>
        <h1 class="page-title">用户会话</h1>
        <p class="page-desc">
          这里只展示转人工后建立的会话。平台客服接入后即可回复，并可按需邀请商家协同。
        </p>
      </div>
      <div class="online-summary">
        <span><i /> 自动刷新中</span>
        <strong>{{ result.total }} 个会话</strong>
      </div>
    </header>

    <div class="conversation-workspace">
      <aside class="conversation-list-panel">
        <div class="filter-tabs">
          <button
            v-for="tab in filterTabs"
            :key="tab.key || 'all'"
            type="button"
            :class="{ 'is-active': statusFilter === tab.key }"
            @click="switchFilter(tab.key)"
          >
            {{ tab.label }}
            <em>{{ tab.count }}</em>
          </button>
        </div>

        <div class="list-search">
          <el-input
            v-model="keyword"
            size="small"
            :prefix-icon="Search"
            placeholder="搜索消费者、订单号或消息"
            clearable
            @keyup.enter="search"
            @clear="search"
          />
        </div>

        <div v-loading="loadingList" class="conversation-list">
          <button
            v-for="conversation in conversations"
            :key="conversation.id"
            type="button"
            class="conversation-item"
            :class="{ 'is-active': conversation.id === selectedId }"
            @click="selectConversation(conversation.id)"
          >
            <span class="conversation-avatar">
              {{ conversation.customer_name.slice(0, 1) }}
              <i v-if="conversation.status === 'waiting'" />
            </span>
            <span class="conversation-copy">
              <span class="conversation-top">
                <strong>{{ conversation.customer_name }}</strong>
                <time>{{ fromNow(conversation.updated_at) }}</time>
              </span>
              <span class="conversation-order">
                {{ conversation.order_product || '售后人工会话' }}
              </span>
              <span class="conversation-preview">
                {{ conversation.last_message || '暂无消息' }}
              </span>
              <span class="conversation-meta">
                <StatusTag kind="conversation" :value="conversation.status" dot />
                <em v-if="conversation.merchant_name" class="merchant-joined">
                  <el-icon><ShoppingBag /></el-icon>
                  商家已加入
                </em>
              </span>
            </span>
          </button>

          <EmptyState
            v-if="!loadingList && conversations.length === 0"
            compact
            title="暂无用户会话"
            description="消费者对 AI 处理结果不满意，或 AI 无法自动处理时，会转入这里。"
          />
        </div>
      </aside>

      <section class="conversation-panel">
        <template v-if="selectedConversation">
          <header class="conversation-head">
            <span class="conversation-head__avatar">
              {{ selectedConversation.customer_name.slice(0, 1) }}
              <i />
            </span>
            <div class="conversation-head__copy">
              <div>
                <h2>{{ selectedConversation.customer_name }}</h2>
                <StatusTag kind="conversation" :value="selectedConversation.status" dot />
                <span v-if="selectedConversation.merchant_name" class="merchant-chip">
                  <el-icon><ShoppingBag /></el-icon>
                  {{ selectedConversation.merchant_name }}
                </span>
              </div>
              <p>
                {{ selectedConversation.order_no || '无关联订单' }}
                <span>·</span>
                {{ selectedConversation.order_product || '售后会话' }}
                <span>·</span>
                {{ selectedConversation.assigned_agent_name || '等待平台客服接入' }}
              </p>
            </div>
            <div class="conversation-actions">
              <el-button
                v-if="selectedConversation.status === 'waiting'"
                type="primary"
                :loading="accepting"
                :icon="Headset"
                @click="acceptConversation"
              >
                接入会话
              </el-button>
              <el-button
                v-if="!hasMerchant && canReply"
                :icon="Plus"
                @click="openInviteDialog"
              >
                邀请商家
              </el-button>
              <button
                v-if="!isClosed"
                type="button"
                class="close-action"
                @click="closeConversation"
              >
                <el-icon><CircleClose /></el-icon>
                结束
              </button>
            </div>
          </header>

          <div v-if="selectedConversation.status === 'waiting'" class="waiting-banner">
            <span><el-icon><Headset /></el-icon></span>
            <div>
              <strong>消费者正在等待接入</strong>
              <p>接入后可以发送消息；接入前仍能看到消费者留下的消息。</p>
            </div>
            <el-button size="small" type="primary" :loading="accepting" @click="acceptConversation">
              立即接入
            </el-button>
          </div>

          <div v-if="isClosed" class="closed-banner">
            <el-icon><CircleClose /></el-icon>
            本次人工会话已结束，只支持查看历史记录。
          </div>

          <ChatStream
            :key="selectedConversation.id"
            :messages="messages"
            current-role="platform"
            empty-title="暂无聊天消息"
            empty-description="消费者与平台客服、商家客服的消息会显示在这里。"
          />

          <ChatComposer
            v-if="canReply"
            v-model="draft"
            :disabled="sending"
            :loading="sending"
            placeholder="回复消费者，Enter 发送…"
            @send="sendMessage"
          />
          <div v-else-if="selectedConversation.status === 'waiting'" class="conversation-footnote">
            <span>请先接入会话，再向消费者发送消息</span>
            <el-button size="small" type="primary" @click="acceptConversation">接入</el-button>
          </div>
          <div v-else class="conversation-footnote is-closed">
            <span>会话已结束，无法继续发送消息</span>
          </div>
        </template>

        <EmptyState
          v-else
          title="选择一个用户会话"
          description="从左侧选择等待接入或人工处理中的会话，开始与消费者沟通。"
        />
      </section>

      <aside v-if="selectedConversation" class="context-panel">
        <div class="context-card">
          <div class="context-card__head">
            <h3><el-icon><User /></el-icon> 消费者信息</h3>
          </div>
          <div class="customer-profile">
            <span>{{ selectedConversation.customer_name.slice(0, 1) }}</span>
            <div>
              <strong>{{ selectedConversation.customer_name }}</strong>
              <small>消费者 ID · C{{ String(selectedConversation.customer_id).padStart(4, '0') }}</small>
            </div>
          </div>
          <dl class="context-info">
            <div>
              <dt>关联订单</dt>
              <dd>{{ selectedConversation.order_no || '—' }}</dd>
            </div>
            <div>
              <dt>商品</dt>
              <dd>{{ selectedConversation.order_product || '—' }}</dd>
            </div>
            <div>
              <dt>处理人</dt>
              <dd>{{ selectedConversation.assigned_agent_name || '待接入' }}</dd>
            </div>
            <div>
              <dt>商家</dt>
              <dd>{{ selectedConversation.merchant_name || '未邀请' }}</dd>
            </div>
          </dl>
        </div>

        <div class="context-card">
          <div class="context-card__head">
            <h3><el-icon><Tickets /></el-icon> 关联工单</h3>
            <span>{{ linkedTickets.length }}</span>
          </div>
          <div v-if="linkedTickets.length" class="linked-tickets">
            <button
              v-for="ticket in linkedTickets"
              :key="ticket.id"
              type="button"
              @click="openTicket(ticket.id)"
            >
              <span class="linked-ticket__icon"><el-icon><Tickets /></el-icon></span>
              <span class="linked-ticket__copy">
                <strong>{{ ticket.subject }}</strong>
                <small>{{ ticket.ticket_no }} · {{ ticketCategoryLabel(ticket.category) }}</small>
              </span>
              <StatusTag kind="ticket" :value="ticket.status" />
              <el-icon class="linked-arrow"><ArrowRight /></el-icon>
            </button>
          </div>
          <EmptyState
            v-else
            compact
            title="无关联工单"
            description="该会话可能由普通咨询转人工建立。"
          />
        </div>

        <div class="context-card context-note">
          <span><el-icon><ChatDotRound /></el-icon></span>
          <p>
            商家加入后可以看到本会话历史消息，但无法查看工单、AI 分析或平台订单模块。
          </p>
        </div>

        <button
          v-if="hasMerchant && !isClosed"
          type="button"
          class="merchant-joined-card"
          disabled
        >
          <el-icon><ShoppingBag /></el-icon>
          {{ selectedConversation.merchant_name }} 已加入
        </button>
      </aside>
    </div>

    <el-dialog
      v-model="inviteVisible"
      class="platform-dialog"
      width="560px"
      title="邀请商家加入会话"
      append-to-body
      :close-on-click-modal="false"
    >
      <div class="invite-tip">
        邀请后，商家可在自己的协同会话中查看历史消息并参与沟通。商家看不到工单信息。
      </div>
      <div class="invite-search">
        <el-input
          v-model="merchantKeyword"
          :prefix-icon="Search"
          placeholder="搜索店铺名称、联系人或手机号"
          clearable
          @keyup.enter="searchMerchants"
          @clear="searchMerchants"
        />
        <el-button type="primary" :loading="merchantLoading" @click="searchMerchants">
          搜索
        </el-button>
      </div>
      <div v-loading="merchantLoading" class="merchant-list">
        <button
          v-for="merchant in merchants"
          :key="merchant.id"
          type="button"
          class="merchant-option"
          :class="{ 'is-selected': selectedMerchantId === merchant.id }"
          @click="selectedMerchantId = merchant.id"
        >
          <span class="merchant-option__icon"><el-icon><ShoppingBag /></el-icon></span>
          <span class="merchant-option__copy">
            <strong>{{ merchant.store_name }}</strong>
            <small>{{ merchant.contact_name || '—' }} · {{ merchant.phone || '无联系电话' }}</small>
          </span>
          <span v-if="selectedMerchantId === merchant.id" class="merchant-option__check">已选择</span>
        </button>
        <p v-if="!merchantLoading && merchants.length === 0" class="empty-merchant">
          没有找到商家
        </p>
      </div>
      <template #footer>
        <el-button @click="inviteVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="inviting"
          :disabled="!selectedMerchantId"
          @click="confirmInvite"
        >
          确认邀请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.conversations-head {
  margin-bottom: 18px;
}

.online-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  color: #9a9aa3;
  font-size: 12px;
}

.online-summary span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.online-summary i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #16b87c;
}

.online-summary strong {
  color: #6e6e77;
  font-size: 12px;
  font-weight: 500;
}

.conversation-workspace {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 300px;
  gap: 12px;
  height: calc(100vh - 68px - 108px);
  min-height: 570px;
}

.conversation-list-panel,
.conversation-panel,
.context-panel {
  min-height: 0;
  border: 1px solid #e8e8ee;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 7px 24px rgba(27, 29, 35, 0.035);
}

.conversation-list-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-tabs {
  display: flex;
  gap: 2px;
  padding: 9px 8px 8px;
  border-bottom: 1px solid #f3f3f6;
  overflow-x: auto;
}

.filter-tabs button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
  height: 32px;
  padding: 0 9px;
  border-radius: 7px;
  color: #96969f;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.filter-tabs button:hover {
  color: #3f5d93;
  background: #f3f7ff;
}

.filter-tabs button.is-active {
  color: #2f6fe4;
  background: #eef4ff;
  font-weight: 600;
}

.filter-tabs em {
  display: grid;
  place-items: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 5px;
  background: rgba(130, 130, 140, 0.09);
  font-size: 11px;
  font-style: normal;
}

.list-search {
  padding: 8px 9px;
}

.list-search :deep(.el-input__wrapper) {
  height: 34px;
  border-radius: 8px;
  background: #fafafb;
  box-shadow: 0 0 0 1px #efeff3 inset;
}

.list-search :deep(.el-input__inner) {
  font-size: 12px;
}

.conversation-list {
  flex: 1;
  min-height: 0;
  padding: 0 6px 8px;
  overflow-y: auto;
}

.conversation-item {
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

.conversation-item:hover {
  background: #f7faff;
}

.conversation-item.is-active {
  border-color: #dbe6f5;
  background: linear-gradient(135deg, #f5f8ff, #eef4ff);
  box-shadow: inset 2px 0 0 #2f6fe4;
}

.conversation-avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  margin-top: 1px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #869ed8, #5a73b7);
  font-size: 12px;
  font-weight: 600;
}

.conversation-avatar i {
  position: absolute;
  top: -1px;
  right: -1px;
  width: 7px;
  height: 7px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #eda000;
}

.conversation-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.conversation-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
}

.conversation-top strong {
  color: #4e4e56;
  font-size: 12px;
  font-weight: 600;
}

.conversation-top time {
  flex: 0 0 auto;
  color: #b2b2ba;
  font-size: 11px;
}

.conversation-order {
  overflow: hidden;
  color: #8f8f98;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-preview {
  overflow: hidden;
  color: #a8a8b0;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: 5px;
}

.conversation-meta :deep(.status-tag) {
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
}

.merchant-joined {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: #0f7b7b;
  font-size: 11px;
  font-style: normal;
}

.conversation-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.conversation-head {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 0 0 auto;
  min-height: 72px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f1f4;
}

.conversation-head__avatar {
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(145deg, #879ed8, #5a72b3);
  font-size: 13px;
  font-weight: 600;
}

.conversation-head__avatar i {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 8px;
  height: 8px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #14b87b;
}

.conversation-head__copy {
  min-width: 0;
  flex: 1;
}

.conversation-head__copy > div {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.conversation-head__copy h2 {
  color: #3f3f46;
  font-size: 13px;
  font-weight: 650;
}

.conversation-head__copy p {
  margin-top: 4px;
  overflow: hidden;
  color: #a3a3ab;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-head__copy p span {
  padding: 0 3px;
  color: #d3d3d9;
}

.merchant-chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 5px;
  border-radius: 3px;
  color: #0c7777;
  background: #eaf8f7;
  font-size: 11px;
}

.conversation-actions {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
}

.conversation-actions :deep(.el-button) {
  height: 34px;
  padding: 0 12px;
  border-radius: 7px;
  font-size: 13px;
}

.close-action {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 4px 0;
  color: #a5a5ad;
  background: transparent;
  font-size: 11px;
  cursor: pointer;
}

.close-action:hover {
  color: #2f6fe4;
}

.waiting-banner {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 0 0 auto;
  margin: 8px 12px 0;
  padding: 8px 10px;
  border: 1px solid #ffe5c3;
  border-radius: 8px;
  background: #fffaf0;
}

.waiting-banner > span {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 7px;
  color: #d28a03;
  background: #fff0d2;
  font-size: 14px;
}

.waiting-banner > div {
  flex: 1;
  min-width: 0;
}

.waiting-banner strong {
  color: #856015;
  font-size: 12px;
}

.waiting-banner p {
  margin-top: 2px;
  color: #b7985d;
  font-size: 11px;
}

.waiting-banner :deep(.el-button) {
  height: 30px;
  font-size: 12px;
}

.closed-banner {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
  margin: 8px 12px 0;
  padding: 7px 9px;
  border-radius: 7px;
  color: #8d8d96;
  background: #f7f7f9;
  font-size: 11px;
}

.conversation-footnote {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 0 0 auto;
  padding: 11px 14px;
  border-top: 1px solid #f2f2f4;
  color: #9f9fa8;
  background: #fbfbfc;
  font-size: 12px;
}

.conversation-footnote.is-closed {
  justify-content: flex-start;
}

.conversation-footnote :deep(.el-button) {
  height: 32px;
  font-size: 12px;
}

.context-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 4px;
  overflow-y: auto;
  border-radius: 13px;
}

.context-card {
  flex: 0 0 auto;
  padding: 14px;
  border: 1px solid #ececf1;
  border-radius: 11px;
  background: #fff;
}

.context-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 9px;
  margin-bottom: 10px;
}

.context-card__head h3 {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606068;
  font-size: 12px;
  font-weight: 650;
}

.context-card__head h3 :deep(.el-icon) {
  color: #a4a4ac;
  font-size: 13px;
}

.context-card__head > span {
  color: #a4a4ac;
  font-size: 11px;
}

.customer-profile {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-profile > span {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #899fd9, #5b72b4);
  font-size: 12px;
  font-weight: 600;
}

.customer-profile > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-profile strong {
  color: #55555d;
  font-size: 12px;
  font-weight: 600;
}

.customer-profile small {
  color: #a6a6ae;
  font-size: 11px;
}

.context-info {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin: 11px 0 0;
  padding-top: 10px;
  border-top: 1px dashed #f0f0f4;
}

.context-info div {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.context-info dt {
  flex: 0 0 auto;
  color: #a4a4ac;
  font-size: 11px;
}

.context-info dd {
  margin: 0;
  overflow: hidden;
  color: #71717a;
  font-size: 11px;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.linked-tickets {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.linked-tickets button {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 6px;
  border: 1px solid transparent;
  border-radius: 7px;
  text-align: left;
  background: transparent;
  cursor: pointer;
}

.linked-tickets button:hover {
  border-color: #dbe6f5;
  background: #f7faff;
}

.linked-ticket__icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  color: #2f6fe4;
  background: #eef4ff;
  font-size: 13px;
}

.linked-ticket__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  flex: 1;
}

.linked-ticket__copy strong {
  overflow: hidden;
  color: #65656e;
  font-size: 11px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.linked-ticket__copy small {
  color: #acacb4;
  font-size: 11px;
}

.linked-tickets :deep(.status-tag) {
  height: 19px;
  padding: 0 5px;
  font-size: 11px;
}

.linked-arrow {
  color: #c4c4cb;
  font-size: 11px;
}

.context-note {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  border: 0;
  background: transparent;
  padding: 0 4px;
}

.context-note > span {
  color: #b5b5bd;
  font-size: 13px;
}

.context-note p {
  color: #aaaab2;
  font-size: 11px;
  line-height: 1.65;
}

.merchant-joined-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 0 0 auto;
  width: 100%;
  height: 34px;
  border: 1px dashed #c8e8e6;
  border-radius: 7px;
  color: #118181;
  background: #f2fafa;
  font-size: 11px;
}

.invite-tip {
  padding: 9px 10px;
  border-radius: 7px;
  color: #5f6f8f;
  background: #f5f8ff;
  font-size: 12px;
  line-height: 1.7;
}

.invite-search {
  display: flex;
  gap: 7px;
  margin-top: 12px;
}

.invite-search :deep(.el-input__wrapper) {
  border-radius: 7px;
}

.invite-search :deep(.el-input__wrapper) {
  height: 36px;
  border-radius: 8px;
}

.invite-search :deep(.el-button) {
  height: 36px;
  border-radius: 8px;
  font-size: 13px;
}

.merchant-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 290px;
  margin-top: 9px;
  overflow-y: auto;
}

.merchant-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 11px;
  border: 1px solid #f0f0f4;
  border-radius: 9px;
  text-align: left;
  background: #fff;
  cursor: pointer;
}

.merchant-option:hover {
  border-color: #dbe6f5;
}

.merchant-option.is-selected {
  border-color: #b9d1f9;
  background: #eef4ff;
}

.merchant-option__icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  color: #0e8583;
  background: #ebf9f8;
  font-size: 15px;
}

.merchant-option__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.merchant-option__copy strong {
  color: #56565e;
  font-size: 12px;
  font-weight: 550;
}

.merchant-option__copy small {
  color: #a5a5ad;
  font-size: 11px;
}

.merchant-option__check {
  padding: 3px 5px;
  border-radius: 4px;
  color: #2f6fe4;
  background: #eef4ff;
  font-size: 11px;
}

.empty-merchant {
  padding: 30px;
  color: #aaaab2;
  font-size: 12px;
  text-align: center;
}

@media (max-width: 1180px) {
  .conversation-workspace {
    grid-template-columns: 300px minmax(0, 1fr);
  }

  .context-panel {
    display: none;
  }
}

@media (max-width: 860px) {
  .conversation-workspace {
    display: flex;
    flex-direction: column;
    height: auto;
  }

  .conversation-list-panel {
    max-height: 240px;
  }

  .conversation-panel {
    min-height: 520px;
    height: calc(100dvh - 280px);
  }

  .conversation-actions :deep(.el-button) {
    display: none;
  }

  .conversation-actions .close-action {
    display: inline-flex;
  }

  .waiting-banner p {
    display: none;
  }
}
</style>
