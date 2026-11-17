<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowRight,
  Box,
  Refresh,
  Search,
  Tickets,
} from '@element-plus/icons-vue'
import type { OrderStatus } from '@/types'
import { useMockStore } from '@/stores/mock'
import { useAdminUiStore } from '@/stores/adminUi'
import {
  formatAmount,
  formatDateTime,
  initials,
  maskPhone,
} from '@/utils/format'
import { orderStatusOptions, ticketTypeLabel } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const mock = useMockStore()
const ui = useAdminUiStore()

const keyword = ref(String(route.query.keyword ?? ''))
const appliedKeyword = ref(keyword.value)
const status = ref<OrderStatus | ''>('')
const page = ref(1)
const pageSize = 8

const orders = computed(() => {
  const term = appliedKeyword.value.trim().toLowerCase()
  return mock.db.orders
    .filter((order) => !status.value || order.orderStatus === status.value)
    .filter((order) => {
      if (!term) return true
      const customer = mock.customerById(order.customerId)
      return [
        order.orderNo,
        order.productName,
        order.productSpec,
        customer?.name ?? '',
        customer?.phone ?? '',
      ]
        .join(' ')
        .toLowerCase()
        .includes(term)
    })
    .sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    )
    .map((order) => {
      const customer = mock.customerById(order.customerId)
      const tickets = mock.ticketsForOrder(order.id)
      return {
        ...order,
        customerName: customer?.name ?? '—',
        customerPhone: customer?.phone ?? '',
        tickets,
        latestTicket: tickets[0],
      }
    })
})

const total = computed(() => orders.value.length)
const pagedOrders = computed(() => {
  const start = (page.value - 1) * pageSize
  return orders.value.slice(start, start + pageSize)
})

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
    page.value = 1
  },
)

watch(
  () => route.query.order,
  (value) => {
    const id = Number(value)
    if (Number.isFinite(id) && mock.orderById(id)) {
      ui.openOrderDrawer(id)
    }
  },
  { immediate: true },
)

function applyFilters(): void {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
}

function resetFilters(): void {
  keyword.value = ''
  appliedKeyword.value = ''
  status.value = ''
  page.value = 1
}

function openOrder(id: number): void {
  ui.openOrderDrawer(id)
}

function handleRowClick(row: { id: number }): void {
  openOrder(row.id)
}
</script>

<template>
  <div class="orders-page">
    <header class="page-head">
      <div>
        <p class="eyebrow">ORDER LOOKUP</p>
        <h1 class="page-title">订单查询</h1>
        <p class="page-desc">
          按订单号、手机号或客户姓名定位订单，查看物流、售后记录并创建工单。
        </p>
      </div>
      <div class="order-summary">
        <span class="order-summary__icon"><el-icon><Box /></el-icon></span>
        <div>
          <strong>{{ total }}</strong>
          <span>笔订单匹配当前条件</span>
        </div>
      </div>
    </header>

    <section class="filter-bar surface-card">
      <div class="filter-field filter-field--search">
        <label>关键词</label>
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          placeholder="订单号 / 手机号 / 客户姓名"
          clearable
          @keyup.enter="applyFilters"
        />
      </div>
      <div class="filter-field">
        <label>订单状态</label>
        <el-select
          v-model="status"
          placeholder="全部状态"
          clearable
          class="status-select"
        >
          <el-option
            v-for="option in orderStatusOptions"
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

    <section class="order-table-card surface-card">
      <div class="table-card-head">
        <div>
          <h2>订单列表</h2>
          <p>数据来自演示订单库，点击行或“查看”可打开订单详情。</p>
        </div>
        <span class="table-count">共 {{ total }} 笔</span>
      </div>

      <el-table
        :data="pagedOrders"
        class="order-table"
        row-key="id"
        @row-click="handleRowClick"
      >
        <el-table-column label="订单号" min-width="158">
          <template #default="{ row }">
            <div class="order-no-cell">
              <strong>{{ row.orderNo }}</strong>
              <span>{{ formatDateTime(row.createdAt) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="商品" min-width="220">
          <template #default="{ row }">
            <div class="product-cell">
              <span class="product-cell__thumb">
                <el-icon><Box /></el-icon>
              </span>
              <span>
                <strong>{{ row.productName }}</strong>
                <small>{{ row.productSpec }} × {{ row.quantity }}</small>
              </span>
            </div>
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

        <el-table-column label="实付金额" width="112" align="right">
          <template #default="{ row }">
            <span class="table-amount">{{ formatAmount(row.amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="104" align="center">
          <template #default="{ row }">
            <StatusTag kind="order" :value="row.orderStatus" dot />
          </template>
        </el-table-column>

        <el-table-column label="售后记录" min-width="150">
          <template #default="{ row }">
            <div v-if="row.latestTicket" class="after-sale-cell">
              <StatusTag kind="ticket" :value="row.latestTicket.status" />
              <span>
                {{ ticketTypeLabel(row.latestTicket.type) }}
                <template v-if="row.tickets.length > 1">
                  · {{ row.tickets.length }} 张
                </template>
              </span>
            </div>
            <span v-else class="empty-value">暂无售后</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="86" fixed="right" align="center">
          <template #default="{ row }">
            <button
              class="view-button"
              type="button"
              @click.stop="openOrder(row.id)"
            >
              查看
              <el-icon><ArrowRight /></el-icon>
            </button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="table-empty">
            <span><el-icon><Tickets /></el-icon></span>
            <p>没有找到符合条件的订单</p>
            <small>尝试更换关键词或清空状态筛选。</small>
          </div>
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-footer__hint">当前展示 {{ pagedOrders.length }} / {{ total }} 笔订单</span>
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
.orders-page {
  height: 100%;
  padding-right: 2px;
  overflow-y: auto;
}

.page-head {
  margin-bottom: 16px;
}

.page-head > div:first-child {
  padding-top: 2px;
}

.order-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 13px;
  border: 1px solid rgba(228, 228, 235, 0.8);
  border-radius: 11px;
  background: #fff;
}

.order-summary__icon {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  color: #df4a2e;
  background: #fff1ee;
  font-size: 15px;
}

.order-summary div {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.order-summary strong {
  color: #3d3d43;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
  line-height: 1;
}

.order-summary span:last-child {
  color: #9b9ba5;
  font-size: 10px;
}

.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  margin-bottom: 14px;
  padding: 15px 17px;
  border-radius: 13px;
  box-shadow: 0 5px 18px rgba(27, 29, 35, 0.03);
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 0 0 180px;
}

.filter-field--search {
  flex: 1;
  max-width: 390px;
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

.status-select {
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

.order-table-card {
  padding: 0;
  overflow: hidden;
  border-radius: 13px;
}

.table-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 15px 18px 13px;
  border-bottom: 1px solid #f3f3f6;
}

.table-card-head h2 {
  color: #3f3f46;
  font-size: 14px;
  font-weight: 650;
}

.table-card-head p {
  margin-top: 4px;
  color: #a2a2ab;
  font-size: 10px;
}

.table-count {
  padding: 4px 8px;
  border-radius: 5px;
  color: #9898a1;
  background: #f7f7f9;
  font-size: 10px;
}

.order-table {
  width: 100%;
  --el-table-header-bg-color: #fbfbfc;
  --el-table-row-hover-bg-color: #fffaf8;
  cursor: pointer;
}

.order-table :deep(th.el-table__cell) {
  height: 41px;
  padding: 0;
  border-bottom-color: #f2f2f5;
  color: #96969f;
  font-size: 11px;
  font-weight: 500;
}

.order-table :deep(td.el-table__cell) {
  padding: 12px 0;
  border-bottom-color: #f5f5f7;
}

.order-table :deep(.el-table__row:last-child td) {
  border-bottom: 0;
}

.order-no-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.order-no-cell strong {
  color: #55555e;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.order-no-cell span {
  color: #ababb3;
  font-size: 10px;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.product-cell__thumb {
  display: grid;
  place-items: center;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #e76c37;
  background: #fff4ed;
  font-size: 15px;
}

.product-cell > span:last-child {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.product-cell strong {
  overflow: hidden;
  color: #515159;
  font-size: 12px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-cell small {
  color: #a8a8b0;
  font-size: 10px;
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

.table-amount {
  color: #d5402f;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
  font-weight: 600;
}

.after-sale-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.after-sale-cell span:last-child {
  color: #a0a0a9;
  font-size: 10px;
}

.after-sale-cell :deep(.status-tag) {
  width: fit-content;
  height: 19px;
  padding: 0 6px;
  font-size: 10px;
}

.empty-value {
  color: #b6b6be;
  font-size: 11px;
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

@media (max-width: 900px) {
  .page-head {
    align-items: flex-start;
  }

  .order-summary {
    display: none;
  }

  .filter-bar {
    flex-wrap: wrap;
  }

  .filter-field {
    flex: 1 1 150px;
  }

  .filter-field--search {
    flex-basis: 100%;
    max-width: none;
  }

  .filter-actions {
    width: 100%;
    margin-left: 0;
  }
}
</style>
