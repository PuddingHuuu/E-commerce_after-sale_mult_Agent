<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  Cpu,
  Refresh,
  Search,
  Tickets,
} from '@element-plus/icons-vue'
import type { Page, Ticket } from '@/types/api'
import { platformApi } from '@/api/platform'
import { showError } from '@/api/http'
import {
  formatDateTime,
  fromNow,
} from '@/utils/format'
import {
  platformTicketGroups,
  ticketCategoryLabel,
} from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'
import PlatformTicketDrawer from '@/components/platform/PlatformTicketDrawer.vue'

const route = useRoute()
const router = useRouter()

const group = ref('ai')
const keyword = ref('')
const appliedKeyword = ref('')
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const result = ref<Page<Ticket>>({
  items: [],
  total: 0,
  page: 1,
  page_size: pageSize,
  counts: {},
})
const drawerVisible = ref(false)
const selectedTicketId = ref<number | null>(null)

const tabs = computed(() =>
  platformTicketGroups.map((tab) => ({
    ...tab,
    count: result.value.counts?.[tab.key] ?? 0,
  })),
)

async function loadTickets(): Promise<void> {
  loading.value = true
  try {
    result.value = await platformApi.getTickets({
      group: group.value,
      keyword: appliedKeyword.value || undefined,
      page: page.value,
      page_size: pageSize,
    })
  } catch (error) {
    showError(error)
  } finally {
    loading.value = false
  }
}

function switchGroup(key: string): void {
  if (group.value === key) return
  group.value = key
  page.value = 1
  void loadTickets()
}

function search(): void {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
  void loadTickets()
}

function changePage(nextPage: number): void {
  page.value = nextPage
  void loadTickets()
}

function openTicket(ticket: Ticket): void {
  selectedTicketId.value = ticket.id
  drawerVisible.value = true
  void router.replace({
    path: '/platform/tickets',
    query: { ...route.query, ticket: String(ticket.id) },
  })
}

function handleUpdated(): void {
  void loadTickets()
}

function handleRowClick(row: Ticket): void {
  openTicket(row)
}

watch(
  () => route.query.ticket,
  (value) => {
    const id = Number(value)
    if (Number.isFinite(id) && id > 0) {
      selectedTicketId.value = id
      drawerVisible.value = true
    }
  },
  { immediate: true },
)

onMounted(loadTickets)
</script>

<template>
  <div class="platform-tickets-page">
    <header class="page-head platform-page-head">
      <div>
        <p class="eyebrow">AFTER-SALE TICKETS</p>
        <h1 class="page-title">工单中心</h1>
        <p class="page-desc">
          统一查看 AI 处理中与转人工的售后工单，支持按工单号、订单号、消费者搜索。
        </p>
      </div>
      <div class="head-hint">
        <span><el-icon><Cpu /></el-icon> AI 先行处理</span>
        <p>分类 · 检索 · 回复</p>
      </div>
    </header>

    <section class="ticket-workspace surface-card">
      <div class="ticket-toolbar">
        <div class="group-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            :class="{ 'is-active': group === tab.key }"
            @click="switchGroup(tab.key)"
          >
            {{ tab.label }}
            <em>{{ tab.count }}</em>
          </button>
        </div>
        <el-button :icon="Refresh" class="refresh-button" @click="loadTickets">
          刷新
        </el-button>
      </div>

      <div class="search-bar">
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          placeholder="搜索工单号、订单号、消费者姓名或手机号"
          clearable
          @keyup.enter="search"
          @clear="search"
        />
        <el-button type="primary" :icon="Search" @click="search">查询</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="result.items"
        class="ticket-table"
        row-key="id"
        @row-click="handleRowClick"
      >
        <el-table-column label="工单信息" min-width="235">
          <template #default="{ row }">
            <div class="ticket-no-cell">
              <div class="ticket-type-line">
                <span class="ticket-dot" />
                <strong>{{ row.subject }}</strong>
              </div>
              <span>{{ row.ticket_no }} · {{ ticketCategoryLabel(row.category) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="消费者" min-width="130">
          <template #default="{ row }">
            <div class="customer-cell">
              <span class="customer-avatar">{{ row.customer_name?.slice(0, 1) || '客' }}</span>
              <div>
                <strong>{{ row.customer_name }}</strong>
                <small>{{ row.customer_phone || '—' }}</small>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="关联订单" min-width="150">
          <template #default="{ row }">
            <span class="order-no">{{ row.order?.order_no || '—' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="当前状态" width="130">
          <template #default="{ row }">
            <StatusTag kind="ticket" :value="row.status" dot />
          </template>
        </el-table-column>

        <el-table-column label="优先级" width="80" align="center">
          <template #default="{ row }">
            <StatusTag kind="priority" :value="row.priority" />
          </template>
        </el-table-column>

        <el-table-column label="处理人" width="100">
          <template #default="{ row }">
            <span class="assignee">{{ row.assignee_name || 'AI' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="更新时间" width="115">
          <template #default="{ row }">
            <div class="updated-cell">
              <span>{{ fromNow(row.updated_at) }}</span>
              <small>{{ formatDateTime(row.updated_at) }}</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <button class="view-link" type="button" @click.stop="openTicket(row)">
              查看
              <el-icon><ArrowRight /></el-icon>
            </button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="table-empty">
            <span><el-icon><Tickets /></el-icon></span>
            <p>没有符合条件的工单</p>
            <small>尝试切换分类或清空搜索词。</small>
          </div>
        </template>
      </el-table>

      <div class="table-footer">
        <span>共 {{ result.total }} 张工单</span>
        <el-pagination
          :current-page="page"
          :page-size="pageSize"
          :total="result.total"
          layout="prev, pager, next"
          background
          hide-on-single-page
          @current-change="changePage"
        />
      </div>
    </section>

    <PlatformTicketDrawer
      v-model="drawerVisible"
      :ticket-id="selectedTicketId"
      @updated="handleUpdated"
    />
  </div>
</template>

<style scoped>
.platform-page-head {
  margin-bottom: 16px;
}

.head-hint {
  flex: 0 0 auto;
  padding: 8px 12px;
  border: 1px solid #ebe7e5;
  border-radius: 10px;
  text-align: right;
  background: rgba(255, 255, 255, 0.7);
}

.head-hint span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6f6f78;
  font-size: 10px;
  font-weight: 550;
}

.head-hint p {
  margin-top: 3px;
  color: #ababb3;
  font-size: 8px;
}

.ticket-workspace {
  padding: 0;
  overflow: hidden;
  border-radius: 14px;
}

.ticket-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 15px;
  border-bottom: 1px solid #f2f2f5;
}

.group-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.group-tabs button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 29px;
  padding: 0 10px;
  border-radius: 6px;
  color: #94949e;
  background: transparent;
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.group-tabs button:hover {
  color: #54545c;
  background: #f7f7f9;
}

.group-tabs button.is-active {
  color: #dc3020;
  background: #fff0ed;
  font-weight: 600;
}

.group-tabs em {
  display: grid;
  place-items: center;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 4px;
  background: rgba(130, 130, 140, 0.09);
  font-size: 8px;
  font-style: normal;
}

.group-tabs button.is-active em {
  color: #dc3020;
  background: rgba(220, 48, 32, 0.09);
}

.refresh-button {
  height: 28px;
  border-radius: 6px;
  font-size: 9px;
}

.search-bar {
  display: flex;
  gap: 8px;
  padding: 10px 15px;
  border-bottom: 1px solid #f5f5f7;
  background: #fcfcfd;
}

.search-bar :deep(.el-input__wrapper) {
  height: 32px;
  border-radius: 7px;
  background: #fff;
  box-shadow: 0 0 0 1px #e9e9ee inset;
}

.search-bar :deep(.el-input__inner) {
  font-size: 10px;
}

.search-bar :deep(.el-button) {
  height: 32px;
  border-radius: 7px;
  font-size: 10px;
}

.ticket-table {
  width: 100%;
  cursor: pointer;
  --el-table-header-bg-color: #fbfbfc;
  --el-table-row-hover-bg-color: #fffaf8;
}

.ticket-table :deep(th.el-table__cell) {
  height: 39px;
  padding: 0;
  border-bottom-color: #f2f2f5;
  color: #9797a0;
  font-size: 9px;
  font-weight: 500;
}

.ticket-table :deep(td.el-table__cell) {
  padding: 10px 0;
  border-bottom-color: #f5f5f7;
}

.ticket-no-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.ticket-type-line {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.ticket-type-line strong {
  overflow: hidden;
  color: #505058;
  font-size: 10px;
  font-weight: 550;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ticket-dot {
  flex: 0 0 6px;
  width: 6px;
  height: 6px;
  border-radius: 2px;
  background: #e24a35;
  transform: rotate(45deg);
}

.ticket-no-cell > span {
  color: #ababb3;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 8px;
}

.customer-cell {
  display: flex;
  align-items: center;
  gap: 7px;
}

.customer-avatar {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 7px;
  color: #6d7ca8;
  background: #f1f4fa;
  font-size: 8px;
  font-weight: 600;
}

.customer-cell > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-cell strong {
  color: #5d5d65;
  font-size: 9px;
  font-weight: 500;
}

.customer-cell small {
  color: #aaaab2;
  font-size: 8px;
}

.order-no {
  color: #8d8d96;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 9px;
}

.assignee {
  color: #83838c;
  font-size: 9px;
}

.updated-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.updated-cell span {
  color: #7e7e87;
  font-size: 9px;
}

.updated-cell small {
  color: #b1b1b9;
  font-size: 8px;
}

.view-link {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  padding: 0;
  color: #9a9aa3;
  background: transparent;
  font-size: 9px;
  cursor: pointer;
}

.view-link:hover {
  color: #db3222;
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 52px 20px;
}

.table-empty > span {
  display: grid;
  place-items: center;
  width: 45px;
  height: 45px;
  border-radius: 13px;
  color: #b3b3bb;
  background: #f6f6f8;
  font-size: 21px;
}

.table-empty p {
  margin-top: 10px;
  color: #85858e;
  font-size: 11px;
}

.table-empty small {
  margin-top: 4px;
  color: #b1b1b9;
  font-size: 9px;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  padding: 12px 15px;
  border-top: 1px solid #f3f3f6;
}

.table-footer > span {
  color: #aaaab2;
  font-size: 9px;
}

.table-footer :deep(.el-pagination) {
  --el-pagination-button-width: 26px;
  --el-pagination-button-height: 26px;
  font-size: 9px;
}

.table-footer :deep(.el-pagination.is-background .btn-prev),
.table-footer :deep(.el-pagination.is-background .btn-next),
.table-footer :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 6px;
  background: #f6f6f8;
}

.table-footer :deep(.el-pagination.is-background .el-pager li.is-active) {
  background: #df3021;
}

@media (max-width: 900px) {
  .head-hint {
    display: none;
  }

  .ticket-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .refresh-button {
    display: none;
  }

  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
