<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowRight,
  Box,
  ChatDotRound,
  Check,
  CircleCheck,
  Close,
  Tickets,
} from '@element-plus/icons-vue'
import { useAdminUiStore } from '@/stores/adminUi'
import { useMockStore } from '@/stores/mock'
import type { TicketPriority, TicketStatus } from '@/types'
import {
  formatAmount,
  formatDateTime,
  fromNow,
  maskPhone,
} from '@/utils/format'
import {
  priorityOptions,
  ticketTypeLabel,
  ticketStatusMeta,
} from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const ui = useAdminUiStore()
const mock = useMockStore()
const router = useRouter()

const visible = computed({
  get: () => ui.ticketDrawerVisible,
  set: (value: boolean) => {
    ui.ticketDrawerVisible = value
  },
})

const ticket = computed(() =>
  ui.selectedTicketId == null ? undefined : mock.ticketById(ui.selectedTicketId),
)

const order = computed(() =>
  ticket.value ? mock.orderById(ticket.value.orderId) : undefined,
)

const customer = computed(() =>
  ticket.value ? mock.customerById(ticket.value.customerId) : undefined,
)

const conversation = computed(() =>
  ticket.value?.conversationId
    ? mock.conversationById(ticket.value.conversationId)
    : undefined,
)

const canStart = computed(() => ticket.value?.status === 'pending')
const canResolve = computed(() => ticket.value?.status === 'processing')
const canClose = computed(
  () => !!ticket.value && !['resolved', 'closed'].includes(ticket.value.status),
)

function updateStatus(status: TicketStatus): void {
  if (!ticket.value) return
  try {
    mock.updateTicket(ticket.value.id, { status })
    ElMessage.success(`工单状态已更新为「${ticketStatusMeta[status].label}」`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '状态更新失败')
  }
}

function handlePriority(value: string | number | boolean | object): void {
  if (!ticket.value) return
  try {
    mock.updateTicket(ticket.value.id, { priority: value as TicketPriority })
    ElMessage.success('优先级已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '优先级更新失败')
  }
}

function viewOrder(): void {
  if (!order.value) return
  ui.openOrderDrawer(order.value.id)
}

function viewConversation(): void {
  if (!conversation.value) return
  ui.ticketDrawerVisible = false
  router.push({
    name: 'admin-workbench',
    query: { session: String(conversation.value.id) },
  })
}
</script>

<template>
  <el-drawer
    v-model="visible"
    class="as-drawer"
    size="540px"
    :with-header="false"
    append-to-body
  >
    <div v-if="ticket" class="entity-drawer">
      <header class="drawer-head">
        <div class="ticket-heading">
          <div class="ticket-heading__icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div>
            <p class="eyebrow">AFTER-SALE TICKET</p>
            <div class="ticket-heading__title">
              <h2>{{ ticketTypeLabel(ticket.type) }}工单</h2>
              <StatusTag kind="ticket" :value="ticket.status" dot />
            </div>
            <p class="ticket-no">{{ ticket.ticketNo }}</p>
          </div>
        </div>
        <button class="drawer-close" type="button" @click="visible = false">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <div class="drawer-scroll">
        <section class="summary-card">
          <div class="summary-card__meta">
            <div>
              <span>客户</span>
              <strong>{{ customer?.name || '—' }}</strong>
            </div>
            <div>
              <span>联系电话</span>
              <strong>{{ customer ? maskPhone(customer.phone) : '—' }}</strong>
            </div>
            <div>
              <span>创建时间</span>
              <strong>{{ formatDateTime(ticket.createdAt) }}</strong>
            </div>
            <div>
              <span>最后更新</span>
              <strong>{{ fromNow(ticket.updatedAt) }}</strong>
            </div>
          </div>
          <div class="summary-card__priority">
            <span>优先级</span>
            <el-select
              :model-value="ticket.priority"
              size="small"
              class="priority-select"
              @change="handlePriority"
            >
              <el-option
                v-for="option in priorityOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            <StatusTag kind="priority" :value="ticket.priority" />
          </div>
        </section>

        <section class="detail-section">
          <div class="detail-section__head">
            <h3>问题描述</h3>
            <span class="assignee">
              处理人
              <strong>{{ ticket.assignee || '未分配' }}</strong>
            </span>
          </div>
          <p class="description">{{ ticket.description }}</p>
        </section>

        <section v-if="order" class="detail-section">
          <div class="detail-section__head">
            <h3>关联订单</h3>
            <button class="inline-action" type="button" @click="viewOrder">
              查看订单
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <button class="linked-card" type="button" @click="viewOrder">
            <span class="linked-card__icon">
              <el-icon><Box /></el-icon>
            </span>
            <span class="linked-card__copy">
              <span class="linked-card__title">{{ order.productName }}</span>
              <span>{{ order.orderNo }} · {{ order.productSpec }}</span>
            </span>
            <span class="linked-card__amount">
              {{ formatAmount(order.amount) }}
              <StatusTag kind="order" :value="order.orderStatus" />
            </span>
          </button>
        </section>

        <section class="detail-section">
          <div class="detail-section__head">
            <h3>处理进度</h3>
          </div>
          <div class="timeline">
            <div class="timeline-item is-done">
              <span class="timeline-dot" />
              <div>
                <strong>工单创建</strong>
                <p>{{ formatDateTime(ticket.createdAt) }}</p>
              </div>
            </div>
            <div
              class="timeline-item"
              :class="{ 'is-done': ['processing', 'resolved'].includes(ticket.status) }"
            >
              <span class="timeline-dot" />
              <div>
                <strong>客服处理中</strong>
                <p>{{ ticket.assignee ? `由 ${ticket.assignee} 跟进` : '等待分配处理人' }}</p>
              </div>
            </div>
            <div
              class="timeline-item"
              :class="{ 'is-done': ticket.status === 'resolved' || ticket.status === 'closed' }"
            >
              <span class="timeline-dot" />
              <div>
                <strong>处理完成</strong>
                <p>
                  {{
                    ticket.resolvedAt
                      ? formatDateTime(ticket.resolvedAt)
                      : '尚未完成'
                  }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section v-if="conversation" class="detail-section">
          <div class="detail-section__head">
            <h3>来源会话</h3>
            <button class="inline-action" type="button" @click="viewConversation">
              进入会话
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <button class="conversation-card" type="button" @click="viewConversation">
            <span class="conversation-card__icon">
              <el-icon><ChatDotRound /></el-icon>
            </span>
            <span class="conversation-card__copy">
              <strong>{{ conversation.title }}</strong>
              <span>{{ conversation.lastMessage }}</span>
            </span>
            <StatusTag kind="conversation" :value="conversation.status" />
          </button>
        </section>
      </div>

      <footer class="drawer-foot">
        <span class="foot-hint">
          <el-icon><CircleCheck /></el-icon>
          {{ ticket.status === 'closed' ? '工单已关闭' : '状态变更实时同步' }}
        </span>
        <div class="foot-actions">
          <el-button
            v-if="canStart"
            type="primary"
            :icon="Tickets"
            @click="updateStatus('processing')"
          >
            开始处理
          </el-button>
          <el-button
            v-if="canResolve"
            type="success"
            :icon="Check"
            @click="updateStatus('resolved')"
          >
            标记已解决
          </el-button>
          <el-button
            v-if="canClose"
            plain
            @click="updateStatus('closed')"
          >
            关闭工单
          </el-button>
          <span v-if="ticket.status === 'resolved'" class="resolved-pill">
            已完成处理
          </span>
        </div>
      </footer>
    </div>

    <EmptyState
      v-else
      title="未找到工单"
      description="该工单可能已被删除或演示数据已重置。"
    />
  </el-drawer>
</template>

<style scoped>
.entity-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f7f8fa;
}

.drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex: 0 0 auto;
  padding: 22px 24px 18px;
  border-bottom: 1px solid #ececf1;
  background: #fff;
}

.ticket-heading {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.ticket-heading__icon {
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  color: #e33525;
  background: linear-gradient(145deg, #fff0ed, #ffe3de);
  font-size: 20px;
}

.ticket-heading__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
}

.ticket-heading h2 {
  color: var(--text-strong);
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.ticket-no {
  margin-top: 4px;
  color: #a3a3ac;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
  letter-spacing: 0.04em;
}

.drawer-close {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #96969f;
  background: #f6f6f8;
  font-size: 16px;
  cursor: pointer;
}

.drawer-close:hover {
  color: #3d3d42;
  background: #eeeef2;
}

.drawer-scroll {
  flex: 1;
  min-height: 0;
  padding: 18px 20px 26px;
  overflow-y: auto;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 16px;
  border: 1px solid #ececf1;
  border-radius: 14px;
  background: #fff;
}

.summary-card__meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  flex: 1;
}

.summary-card__meta div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-card__meta span {
  color: #a3a3ac;
  font-size: 9px;
}

.summary-card__meta strong {
  color: #55555e;
  font-size: 11px;
  font-weight: 500;
}

.summary-card__priority {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex: 0 0 auto;
  padding-left: 15px;
  border-left: 1px solid #f0f0f4;
}

.summary-card__priority > span {
  color: #a3a3ac;
  font-size: 9px;
}

.priority-select {
  width: 90px;
}

.detail-section {
  margin-top: 14px;
  padding: 16px;
  border: 1px solid #ececf1;
  border-radius: 14px;
  background: #fff;
}

.detail-section__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 13px;
}

.detail-section__head h3 {
  color: #3a3a40;
  font-size: 12px;
  font-weight: 650;
}

.assignee {
  color: #a3a3ac;
  font-size: 10px;
}

.assignee strong {
  margin-left: 5px;
  color: #5f5f69;
  font-weight: 500;
}

.inline-action {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 0;
  color: #96969f;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.inline-action:hover {
  color: var(--admin-brand);
}

.description {
  padding: 12px 13px;
  border-left: 3px solid #f3b59e;
  border-radius: 0 9px 9px 0;
  color: #5f5f68;
  background: #fbfaf9;
  font-size: 12px;
  line-height: 1.8;
}

.linked-card,
.conversation-card {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: 1px solid #f0f0f4;
  border-radius: 10px;
  text-align: left;
  background: #fff;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.linked-card:hover,
.conversation-card:hover {
  border-color: #ffd6c4;
  background: #fffaf7;
}

.linked-card__icon,
.conversation-card__icon {
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: #e35b37;
  background: #fff3ed;
  font-size: 16px;
}

.linked-card__copy,
.conversation-card__copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.linked-card__title,
.conversation-card__copy strong {
  overflow: hidden;
  color: #4f4f58;
  font-size: 11px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.linked-card__copy > span,
.conversation-card__copy > span {
  overflow: hidden;
  color: #a3a3ac;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.linked-card__amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex: 0 0 auto;
  color: #d6372b;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
  font-weight: 600;
}

.linked-card__amount :deep(.status-tag),
.conversation-card :deep(.status-tag) {
  height: 18px;
  padding: 0 6px;
  font-size: 9px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-left: 6px;
}

.timeline-item {
  position: relative;
  display: flex;
  gap: 13px;
  padding-bottom: 16px;
  color: #b2b2ba;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item::before {
  content: '';
  position: absolute;
  top: 12px;
  bottom: 0;
  left: 4px;
  width: 1px;
  background: #ececf1;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-dot {
  position: relative;
  z-index: 1;
  flex: 0 0 9px;
  width: 9px;
  height: 9px;
  margin-top: 3px;
  border: 2px solid #dcdce3;
  border-radius: 50%;
  background: #fff;
}

.timeline-item.is-done .timeline-dot {
  border-color: var(--admin-brand);
  background: var(--admin-brand);
  box-shadow: 0 0 0 3px rgba(225, 37, 27, 0.08);
}

.timeline-item strong {
  color: #86868f;
  font-size: 11px;
  font-weight: 500;
}

.timeline-item.is-done strong {
  color: #47474e;
}

.timeline-item p {
  margin-top: 3px;
  font-size: 10px;
}

.drawer-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex: 0 0 auto;
  padding: 13px 20px;
  border-top: 1px solid #ececf1;
  background: #fff;
}

.foot-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #a5a5ae;
  font-size: 9px;
}

.foot-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.resolved-pill {
  padding: 5px 9px;
  border-radius: 6px;
  color: #0f8e63;
  background: #eaf8f1;
  font-size: 10px;
  font-weight: 600;
}

@media (max-width: 640px) {
  .summary-card {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-card__priority {
    flex-direction: row;
    align-items: center;
    padding: 10px 0 0;
    border-top: 1px solid #f0f0f4;
    border-left: 0;
  }

  .drawer-foot {
    align-items: flex-end;
    padding: 12px;
  }

  .foot-hint {
    display: none;
  }

  .foot-actions {
    flex-wrap: wrap;
  }
}
</style>
