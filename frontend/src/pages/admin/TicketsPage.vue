<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  Refresh,
  Search,
  Tickets,
} from '@element-plus/icons-vue'
import type {
  TicketPriority,
  TicketStatus,
  TicketType,
} from '@/types'
import { useMockStore } from '@/stores/mock'
import { useAdminUiStore } from '@/stores/adminUi'
import {
  formatDateTime,
  fromNow,
  initials,
  maskPhone,
} from '@/utils/format'
import {
  priorityOptions,
  ticketStatusMeta,
  ticketStatusOptions,
  ticketTypeLabel,
  ticketTypeOptions,
} from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'

type StatusTab = TicketStatus | 'all'

const route = useRoute()
const router = useRouter()
const mock = useMockStore()
const ui = useAdminUiStore()

const activeStatus = ref<StatusTab>('all')
const keyword = ref(String(route.query.keyword ?? ''))
const appliedKeyword = ref(keyword.value)
const priority = ref<TicketPriority | ''>('')
const type = ref<TicketType | ''>('')
const page = ref(1)
const pageSize = 8

const statusTabs = computed(() => [
  { key: 'all' as StatusTab, label: '全部', count: mock.db.tickets.length },
  ...ticketStatusOptions.map((option) => ({
    key: option.value as StatusTab,
    label: option.label,
    count: mock.db.tickets.filter((ticket) => ticket.status === option.value).length,
  })),
])

const filteredTickets = computed(() => {
  const term = appliedKeyword.value.trim().toLowerCase()
  return mock.db.tickets
    .filter((ticket) => activeStatus.value === 'all' || ticket.status === activeStatus.value)
    .filter((ticket) => !priority.value || ticket.priority === priority.value)
    .filter((ticket) => !type.value || ticket.type === type.value)
    .filter((ticket) => {
      if (!term) return true
      const customer = mock.customerById(ticket.customerId)
      const order = mock.orderById(ticket.orderId)
      return [
        ticket.ticketNo,
        order?.orderNo ?? '',
        customer?.name ?? '',
        customer?.phone ?? '',
        ticket.description,
      ]
        .join(' ')
        .toLowerCase()
        .includes(term)
    })
    .sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    )
    .map((ticket) => {
      const customer = mock.customerById(ticket.customerId)
      const order = mock.orderById(ticket.orderId)
      return {
        ...ticket,
        customerName: customer?.name ?? '—',
        customerPhone: customer?.phone ?? '',
        orderNo: order?.orderNo ?? '—',
      }
    })
})

const total = computed(() => filteredTickets.value.length)
const pagedTickets = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredTickets.value.slice(start, start + pageSize)
})

const activeStatusLabel = computed(() =>
  activeStatus.value === 'all'
    ? '全部'
    : ticketStatusMeta[activeStatus.value].label,
)

watch(
  () => [activeStatus.value, appliedKeyword.value, priority.value, type.value],
  () => {
    page.value = 1
  },
)

watch(total, () => {
  const maxPage = Math.max(1, Math.ceil(total.value / pageSize))
  if (page.value > maxPage) page.value = maxPage
})

watch(
  () => route.query.keyword,
  (value) => {
    const next = String(value ?? '')
    keyword.value = next
    appliedKeyword.value = next
    activeStatus.value = 'all'
    page.value = 1
  },
)

watch(
  () => route.query.ticket,
  (value) => {
    const id = Number(value)
    if (Number.isFinite(id) && mock.ticketById(id)) {
      ui.openTicketDrawer(id)
    }
  },
  { immediate: true },
)

function applyFilters(): void {
  appliedKeyword.value = keyword.value.trim()
}

function resetFilters(): void {
  keyword.value = ''
  appliedKeyword.value = ''
  priority.value = ''
  type.value = ''
  activeStatus.value = 'all'
  page.value = 1
}

function switchStatus(status: StatusTab): void {
  activeStatus.value = status
}

function openTicket(id: number): void {
  ui.openTicketDrawer(id)
}

function handleRowClick(row: { id: number }): void {
  openTicket(row.id)
}

function goWorkbench(): void {
  router.push({ name: 'admin-workbench' })
}
</script>

<template>
  <div class="tickets-page">
    <header class="page-head">
      <div>
        <p class="eyebrow">AFTER-SALE TICKETS</p>
        <h1 class="page-title">售后工单</h1>
        <p class="page-desc">
          查询和处理售后工单，追踪状态流转，并联动查看关联订单与来源会话。
        </p>
      </div>
      <button class="workbench-shortcut" type="button" @click="goWorkbench">
        <span><el-icon><Tickets /></el-icon></span>
        <div>
          <strong>从会话创建工单</strong>
          <small>进入工作台处理客户需求</small>
        </div>
        <el-icon class="shortcut-arrow"><ArrowRight /></el-icon>
      </button>
    </header>

    <section class="filter-bar surface-card">
      <div class="filter-field filter-field--search">
        <label>关键词</label>
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          placeholder="工单号 / 订单号 / 客户姓名"
          clearable
          @keyup.enter="applyFilters"
        />
      </div>
      <div class="filter-field">
        <label>工单类型</label>
        <el-select v-model="type" placeholder="全部类型" clearable class="filter-select">
          <el-option
            v-for="option in ticketTypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>
      <div class="filter-field filter-field--short">
        <label>优先级</label>
        <el-select v-model="priority" placeholder="全部优先级" clearable class="filter-select">
          <el-option
            v-for="option in priorityOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>
      <div class="filter-actions">
        <el-button type="primary" :icon="Search" @click="applyFilters">查询</el-button>
        <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
      </div>
    </section>

    <section class="ticket-table-card surface-card">
      <div class="ticket-tabs-bar">
        <div class="ticket-tabs">
          <button
            v-for="tab in statusTabs"
            :key="tab.key"
            type="button"
            :class="{ 'is-active': activeStatus === tab.key }"
            @click="switchStatus(tab.key)"
          >
            {{ tab.label }}
            <em>{{ tab.count }}</em>
          </button>
        </div>
        <span class="ticket-total">{{ total }} 张工单</span>
      </div>

      <el-table
        :data="pagedTickets"
        class="ticket-table"
        row-key="id"
        @row-click="handleRowClick"
      >
        <el-table-column label="工单信息" min-width="190">
          <template #default="{ row }">
            <div class="ticket-no-cell">
              <div class="ticket-no-line">
                <span class="ticket-type-dot" />
                <strong>{{ ticketTypeLabel(row.type) }}</strong>
              </div>
              <span class="ticket-no">{{ row.ticketNo }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="关联订单" min-width="150">
          <template #default="{ row }">
            <span class="order-link" @click.stop="ui.openOrderDrawer(row.orderId)">
              {{ row.orderNo }}
              <el-icon><ArrowRight /></el-icon>
            </span>
          </template>
        </el-table-column>

        <el-table-column label="客户" min-width="150">
          <template #default="{ row }">
            <div class="customer-cell">
              <span class="customer-cell__avatar">{{ initials(row.customerName) }}</span>
              <span>
                <strong>{{ row.customerName }}</strong>
                <small>{{ maskPhone(row.customerPhone) }}</small>
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="优先级" width="82" align="center">
          <template #default="{ row }">
            <StatusTag kind="priority" :value="row.priority" />
          </template>
        </el-table-column>

        <el-table-column label="状态" width="92" align="center">
          <template #default="{ row }">
            <StatusTag kind="ticket" :value="row.status" dot />
          </template>
        </el-table-column>

        <el-table-column label="处理人" width="98">
          <template #default="{ row }">
            <span class="assignee-cell">{{ row.assignee || '未分配' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="最近更新" width="104">
          <template #default="{ row }">
            <div class="updated-cell">
              <span>{{ fromNow(row.updatedAt) }}</span>
              <small>{{ formatDateTime(row.updatedAt) }}</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="86" fixed="right" align="center">
          <template #default="{ row }">
            <button
              class="view-button"
              type="button"
              @click.stop="openTicket(row.id)"
            >
              处理
              <el-icon><ArrowRight /></el-icon>
            </button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="table-empty">
            <span><el-icon><Tickets /></el-icon></span>
            <p>没有找到符合条件的工单</p>
            <small>更换状态或筛选条件后再试。</small>
          </div>
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-footer__hint">
          当前展示 {{ pagedTickets.length }} / {{ total }} 张工单
          <template v-if="activeStatus !== 'all'">
            · {{ activeStatusLabel }}
          </template>
        </span>
        <el-pagination
          v-model:current-page="page"
          background
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          hide-on-single-page
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.tickets-page {
  height: 100%;
  padding-right: 2px;
  overflow-y: auto;
}

.page-head {
  margin-bottom: 16px;
}

.workbench-shortcut {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid rgba(228, 228, 235, 0.8);
  border-radius: 11px;
  text-align: left;
  background: #fff;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.workbench-shortcut:hover {
  border-color: #ffd9d4;
  background: #fffaf9;
}

.workbench-shortcut > span {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  color: #d83b2a;
  background: #fff0ee;
  font-size: 15px;
}

.workbench-shortcut div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workbench-shortcut strong {
  color: #55555e;
  font-size: 11px;
  font-weight: 600;
}

.workbench-shortcut small {
  color: #a3a3ac;
  font-size: 10px;
}

.shortcut-arrow {
  margin-left: 13px;
  color: #b0b0b8;
  font-size: 12px;
}

.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 14px;
  padding: 15px 17px;
  border-radius: 13px;
  box-shadow: 0 5px 18px rgba(27, 29, 35, 0.03);
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 0 0 154px;
}

.filter-field--search {
  flex: 1;
  max-width: 340px;
}

.filter-field--short {
  flex-basis: 132px;
}

.filter-field label {
  color: #8d8d96;
  font-size: 10px;
  font-weight: 500;
}

.filter-field :deep(.el-input__wrapper),
.filter-field :deep(.el-select__wrapper) {
  height: 34px;
  border-radius: 7px;
  box-shadow: 0 0 0 1px #e9e9ee inset;
}

.filter-field :deep(.el-input__inner),
.filter-field :deep(.el-select__placeholder),
.filter-field :deep(.el-select__selected-item) {
  font-size: 12px;
}

.filter-select {
  width: 100%;
}

.filter-actions {
  display: flex;
  gap: 7px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 34px;
  border-radius: 7px;
  font-size: 12px;
}

.ticket-table-card {
  padding: 0;
  overflow: hidden;
  border-radius: 13px;
}

.ticket-tabs-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 11px 16px;
  border-bottom: 1px solid #f3f3f6;
}

.ticket-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ticket-tabs button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 29px;
  padding: 0 10px;
  border-radius: 6px;
  color: #93939c;
  background: transparent;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition:
    color 0.18s ease,
    background 0.18s ease;
}

.ticket-tabs button:hover {
  color: #55555e;
  background: #f8f8fa;
}

.ticket-tabs button.is-active {
  color: var(--admin-brand);
  background: #fff1ef;
  font-weight: 600;
}

.ticket-tabs em {
  display: grid;
  place-items: center;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 4px;
  background: rgba(115, 115, 125, 0.09);
  font-size: 9px;
  font-style: normal;
}

.ticket-tabs button.is-active em {
  color: var(--admin-brand);
  background: rgba(225, 37, 27, 0.09);
}

.ticket-total {
  color: #a3a3ac;
  font-size: 10px;
}

.ticket-table {
  width: 100%;
  --el-table-header-bg-color: #fbfbfc;
  --el-table-row-hover-bg-color: #fffaf8;
  cursor: pointer;
}

.ticket-table :deep(th.el-table__cell) {
  height: 41px;
  padding: 0;
  border-bottom-color: #f2f2f5;
  color: #96969f;
  font-size: 11px;
  font-weight: 500;
}

.ticket-table :deep(td.el-table__cell) {
  padding: 12px 0;
  border-bottom-color: #f5f5f7;
}

.ticket-table :deep(.el-table__row:last-child td) {
  border-bottom: 0;
}

.ticket-no-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ticket-no-line {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ticket-type-dot {
  width: 6px;
  height: 6px;
  border-radius: 2px;
  background: #e34a32;
  transform: rotate(45deg);
}

.ticket-no-line strong {
  color: #515159;
  font-size: 12px;
  font-weight: 550;
}

.ticket-no {
  color: #ababb3;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
  letter-spacing: 0.03em;
}

.order-link {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  color: #8c8c95;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
  cursor: pointer;
}

.order-link:hover {
  color: var(--admin-brand);
}

.customer-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-cell__avatar {
  display: grid;
  place-items: center;
  width: 25px;
  height: 25px;
  border-radius: 7px;
  color: #6578b6;
  background: #f0f3fb;
  font-size: 9px;
  font-weight: 600;
}

.customer-cell > span:last-child {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-cell strong {
  color: #5c5c64;
  font-size: 12px;
  font-weight: 500;
}

.customer-cell small {
  color: #aaaab2;
  font-size: 10px;
}

.ticket-table :deep(.status-tag) {
  height: 20px;
  padding: 0 6px;
  font-size: 10px;
}

.assignee-cell {
  color: #85858e;
  font-size: 11px;
}

.updated-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.updated-cell span {
  color: #7f7f88;
  font-size: 10px;
}

.updated-cell small {
  color: #b2b2b9;
  font-size: 9px;
}

.view-button {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  padding: 0;
  color: #9b9ba4;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.view-button:hover {
  color: var(--admin-brand);
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 46px 16px;
}

.table-empty > span {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 13px;
  color: #b3b3bb;
  background: #f6f6f8;
  font-size: 20px;
}

.table-empty p {
  margin-top: 11px;
  color: #85858f;
  font-size: 12px;
  font-weight: 500;
}

.table-empty small {
  margin-top: 4px;
  color: #b1b1b9;
  font-size: 10px;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 18px;
  border-top: 1px solid #f3f3f6;
}

.table-footer__hint {
  color: #ababb3;
  font-size: 10px;
}

.table-footer :deep(.el-pagination) {
  --el-pagination-button-height: 26px;
  --el-pagination-button-width: 26px;
  font-size: 10px;
}

.table-footer :deep(.el-pagination.is-background .btn-next),
.table-footer :deep(.el-pagination.is-background .btn-prev),
.table-footer :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 6px;
  background: #f6f6f8;
}

.table-footer :deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--admin-brand);
}

@media (max-width: 1050px) {
  .workbench-shortcut {
    display: none;
  }

  .filter-bar {
    flex-wrap: wrap;
  }

  .filter-field {
    flex: 1 1 140px;
  }

  .filter-field--search {
    flex-basis: 100%;
    max-width: none;
  }

  .filter-actions {
    width: 100%;
    margin-left: 0;
  }

  .ticket-tabs-bar {
    align-items: flex-start;
    flex-direction: column;
    gap: 9px;
  }

  .ticket-total {
    align-self: flex-end;
  }
}
</style>
