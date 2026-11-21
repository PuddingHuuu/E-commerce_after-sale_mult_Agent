<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  MagicStick,
  Plus,
  Tickets,
} from '@element-plus/icons-vue'
import type { Page, Ticket } from '@/types/api'
import { buyerApi } from '@/api/buyer'
import { showError } from '@/api/http'
import { formatDateTime, fromNow } from '@/utils/format'
import { ticketCategoryLabel } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import AfterSaleDialog from '@/components/buyer/AfterSaleDialog.vue'

const router = useRouter()

const result = ref<Page<Ticket>>({
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
  counts: {},
})
const loading = ref(false)
const page = ref(1)
const pageSize = 10
const dialogVisible = ref(false)
let timer: number | null = null

const summary = computed(() => [
  { label: 'AI 处理中', value: result.value.counts?.ai_processing ?? 0, accent: 'blue' },
  { label: '待确认结果', value: result.value.counts?.awaiting_feedback ?? 0, accent: 'violet' },
  { label: '人工处理中', value: (result.value.counts?.waiting_human ?? 0) + (result.value.counts?.human_processing ?? 0), accent: 'green' },
  { label: '已完成', value: (result.value.counts?.resolved ?? 0) + (result.value.counts?.closed ?? 0), accent: 'gray' },
])

async function loadTickets(silent = false): Promise<void> {
  if (!silent) loading.value = true
  try {
    result.value = await buyerApi.listTickets({ page: page.value, page_size: pageSize })
  } catch (error) {
    if (!silent) showError(error)
  } finally {
    loading.value = false
  }
}

function changePage(nextPage: number): void {
  page.value = nextPage
  void loadTickets()
}

function openDetail(ticket: Ticket): void {
  router.push(`/consumer/after-sales/${ticket.id}`)
}

function handleCreated(ticket: Ticket): void {
  router.push(`/consumer/after-sales/${ticket.id}`)
}

onMounted(() => {
  void loadTickets()
  timer = window.setInterval(() => void loadTickets(true), 4000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="buyer-tickets-page">
    <header class="buyer-page-head">
      <div>
        <p class="eyebrow">AFTER-SALES</p>
        <h1>售后服务</h1>
        <p>提交售后后由 AI 先行处理；对结果不满意时，再转人工继续沟通。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="dialogVisible = true">
        申请售后
      </el-button>
    </header>

    <section class="after-sale-summary">
      <div v-for="item in summary" :key="item.label" class="summary-item">
        <span :class="`is-${item.accent}`" />
        <div>
          <strong>{{ item.value }}</strong>
          <small>{{ item.label }}</small>
        </div>
      </div>
    </section>

    <section v-loading="loading" class="ticket-list-area">
      <div v-if="result.items.length" class="ticket-list">
        <button
          v-for="ticket in result.items"
          :key="ticket.id"
          type="button"
          class="ticket-card"
          @click="openDetail(ticket)"
        >
          <div class="ticket-card__head">
            <span class="ticket-card__icon">
              <el-icon><Tickets /></el-icon>
            </span>
            <div class="ticket-card__title">
              <div>
                <h2>{{ ticket.subject }}</h2>
                <StatusTag kind="ticket" :value="ticket.status" dot />
              </div>
              <p>
                售后单号 {{ ticket.ticket_no }}
                <span>·</span>
                {{ ticket.order?.order_no || '关联订单' }}
                <span>·</span>
                {{ ticketCategoryLabel(ticket.category) }}
              </p>
            </div>
            <el-icon class="ticket-card__arrow"><ArrowRight /></el-icon>
          </div>

          <div class="ticket-card__body">
            <p>{{ ticket.description }}</p>
            <div v-if="ticket.ai_reply" class="ai-brief">
              <span><el-icon><MagicStick /></el-icon> AI 处理建议</span>
              <p>{{ ticket.ai_reply }}</p>
            </div>
          </div>

          <div class="ticket-card__foot">
            <span>
              更新于 {{ fromNow(ticket.updated_at) }}
              <template v-if="ticket.conversation_id"> · 已进入人工会话</template>
            </span>
            <span class="ticket-time">{{ formatDateTime(ticket.created_at) }} 提交</span>
          </div>
        </button>
      </div>

      <EmptyState
        v-else-if="!loading"
        title="还没有售后记录"
        description="当收到的商品需要退款、退货、换货或维修时，可以提交售后申请。"
      >
        <el-button type="primary" :icon="Plus" @click="dialogVisible = true">
          申请售后
        </el-button>
      </EmptyState>

      <div v-if="result.total > pageSize" class="ticket-pagination">
        <span>共 {{ result.total }} 条售后记录</span>
        <el-pagination
          :current-page="page"
          :page-size="pageSize"
          :total="result.total"
          layout="prev, pager, next"
          background
          @current-change="changePage"
        />
      </div>
    </section>

    <AfterSaleDialog v-model="dialogVisible" @created="handleCreated" />
  </div>
</template>

<style scoped>
.buyer-page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.buyer-page-head h1 {
  margin-top: 4px;
  color: #27272d;
  font-size: 27px;
  font-weight: 750;
  letter-spacing: -0.03em;
}

.buyer-page-head p:last-child {
  margin-top: 8px;
  color: #92929c;
  font-size: 14px;
}

.buyer-page-head :deep(.el-button) {
  height: 42px;
  padding: 0 19px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 8px 18px rgba(168, 117, 95, 0.18);
}

.after-sale-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 13px;
  padding: 11px;
  border: 1px solid #ececf1;
  border-radius: 12px;
  background: #fff;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 5px 9px;
  border-right: 1px solid #f1f1f4;
}

.summary-item:last-child {
  border-right: 0;
}

.summary-item > span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.summary-item .is-blue {
  background: #2f6fe4;
}

.summary-item .is-violet {
  background: #8b6bd8;
}

.summary-item .is-green {
  background: #0f9f6e;
}

.summary-item .is-gray {
  background: #b0b0b8;
}

.summary-item div {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.summary-item strong {
  color: #3d3d44;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
}

.summary-item small {
  color: #9b9ba4;
  font-size: 12px;
}

.ticket-list-area {
  min-height: 260px;
}

.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.ticket-card {
  display: block;
  width: 100%;
  overflow: hidden;
  border: 1px solid #ececf1;
  border-radius: 14px;
  text-align: left;
  background: #fff;
  box-shadow: 0 7px 22px rgba(28, 29, 35, 0.035);
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.ticket-card:hover {
  border-color: #e7d8ce;
  box-shadow: 0 12px 30px rgba(28, 29, 35, 0.065);
  transform: translateY(-1px);
}

.ticket-card__head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px 13px;
  border-bottom: 1px solid #f5f5f7;
}

.ticket-card__icon {
  display: grid;
  place-items: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #a8755f;
  background: #f7f1ec;
  font-size: 17px;
}

.ticket-card__title {
  min-width: 0;
  flex: 1;
}

.ticket-card__title > div {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ticket-card__title h2 {
  color: #3f3f46;
  font-size: 14px;
  font-weight: 650;
}

.ticket-card__title p {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 5px;
  color: #a2a2ab;
  font-size: 12px;
}

.ticket-card__title p span {
  color: #d1d1d7;
}

.ticket-card__arrow {
  margin-top: 9px;
  color: #c2c2c9;
  font-size: 14px;
}

.ticket-card__body {
  padding: 12px 16px;
}

.ticket-card__body > p {
  color: #66666f;
  font-size: 13px;
  line-height: 1.75;
}

.ai-brief {
  margin-top: 10px;
  padding: 9px 11px;
  border-left: 3px solid #d8bfae;
  border-radius: 0 8px 8px 0;
  background: #faf6f2;
}

.ai-brief > span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #99664f;
  font-size: 12px;
  font-weight: 600;
}

.ai-brief > p {
  display: -webkit-box;
  margin-top: 4px;
  overflow: hidden;
  color: #8c7b70;
  font-size: 12px;
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.ticket-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 16px;
  border-top: 1px solid #f6f6f8;
  color: #a7a7af;
  background: #fcfcfd;
  font-size: 12px;
}

.ticket-time {
  flex: 0 0 auto;
}

.ticket-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-top: 15px;
}

.ticket-pagination > span {
  color: #a8a8b0;
  font-size: 12px;
}

.ticket-pagination :deep(.el-pagination) {
  --el-pagination-button-width: 32px;
  --el-pagination-button-height: 32px;
  font-size: 12px;
}

.ticket-pagination :deep(.el-pagination.is-background .btn-prev),
.ticket-pagination :deep(.el-pagination.is-background .btn-next),
.ticket-pagination :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 7px;
  background: #fff;
  box-shadow: 0 0 0 1px #ececf1 inset;
}

.ticket-pagination :deep(.el-pagination.is-background .el-pager li.is-active) {
  color: #fff;
  background: #b07d62;
  box-shadow: none;
}

@media (max-width: 720px) {
  .buyer-page-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 13px;
  }

  .buyer-page-head h1 {
    font-size: 23px;
  }

  .buyer-page-head :deep(.el-button) {
    width: 100%;
  }

  .after-sale-summary {
    flex-wrap: wrap;
  }

  .summary-item {
    flex: 1 1 42%;
    border-right: 0;
  }

  .ticket-card__foot {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .ticket-pagination {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
