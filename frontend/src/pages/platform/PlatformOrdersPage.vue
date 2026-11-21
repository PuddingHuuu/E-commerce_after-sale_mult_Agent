<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  Box,
  Location,
  Search,
} from '@element-plus/icons-vue'
import type { Order, Page } from '@/types/api'
import { platformApi } from '@/api/platform'
import { showError } from '@/api/http'
import {
  formatAmount,
  formatDateTime,
  maskPhone,
} from '@/utils/format'
import { orderStatusMeta } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'

const keyword = ref('')
const appliedKeyword = ref('')
const orderStatus = ref('')
const loading = ref(false)
const page = ref(1)
const pageSize = 10
const result = ref<Page<Order>>({
  items: [],
  total: 0,
  page: 1,
  page_size: pageSize,
})

const statusOptions = Object.entries(orderStatusMeta).map(([value, meta]) => ({
  value,
  label: meta.label,
}))

async function loadOrders(): Promise<void> {
  loading.value = true
  try {
    result.value = await platformApi.getOrders({
      keyword: appliedKeyword.value || undefined,
      status: orderStatus.value || undefined,
      page: page.value,
      page_size: pageSize,
    })
  } catch (error) {
    showError(error)
  } finally {
    loading.value = false
  }
}

function search(): void {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
  void loadOrders()
}

function reset(): void {
  keyword.value = ''
  appliedKeyword.value = ''
  orderStatus.value = ''
  page.value = 1
  void loadOrders()
}

function changePage(nextPage: number): void {
  page.value = nextPage
  void loadOrders()
}

function afterSaleLabel(status: string): string {
  if (status === 'processing') return '售后处理中'
  if (status === 'completed') return '售后已完成'
  if (status === 'rejected') return '售后已拒绝'
  return '暂无售后'
}

onMounted(loadOrders)
</script>

<template>
  <div class="platform-orders-page">
    <header class="page-head platform-page-head">
      <div>
        <p class="eyebrow">ORDER LOOKUP</p>
        <h1 class="page-title">订单查询</h1>
        <p class="page-desc">
          查询全部演示订单与订单明细，支持订单号、消费者、手机号和商品名称搜索。
        </p>
      </div>
      <div class="order-count">
        <span><el-icon><Box /></el-icon></span>
        <div>
          <strong>{{ result.total }}</strong>
          <small>符合当前条件</small>
        </div>
      </div>
    </header>

    <section class="filter-bar surface-card">
      <div class="filter-field filter-field--search">
        <label>关键词</label>
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          placeholder="订单号 / 消费者 / 手机号 / 商品"
          clearable
          @keyup.enter="search"
        />
      </div>
      <div class="filter-field">
        <label>订单状态</label>
        <el-select v-model="orderStatus" class="status-select" placeholder="全部状态" clearable>
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>
      <div class="filter-actions">
        <el-button type="primary" :icon="Search" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>
    </section>

    <section class="order-table-card surface-card">
      <div class="table-head">
        <h2>订单列表</h2>
        <p>点击行首展开可以查看商品明细、收货信息和物流信息。</p>
      </div>

      <el-table
        v-loading="loading"
        :data="result.items"
        row-key="id"
        class="order-table"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-panel">
              <div class="expand-block">
                <h4>商品明细</h4>
                <div
                  v-for="item in row.items"
                  :key="item.id"
                  class="expand-item"
                >
                  <span class="expand-item__icon"><el-icon><Box /></el-icon></span>
                  <span class="expand-item__copy">
                    <strong>{{ item.product_name }}</strong>
                    <small>{{ item.sku_spec }} · 数量 {{ item.quantity }}</small>
                  </span>
                  <span class="expand-item__price">{{ formatAmount(item.pay_amount) }}</span>
                </div>
              </div>
              <div class="expand-block">
                <h4>履约信息</h4>
                <dl class="expand-info">
                  <div>
                    <dt>收货人</dt>
                    <dd>{{ row.receiver_name }} · {{ maskPhone(row.receiver_phone) }}</dd>
                  </div>
                  <div>
                    <dt>收货地址</dt>
                    <dd>{{ row.receiver_city }} {{ row.receiver_address }}</dd>
                  </div>
                  <div>
                    <dt>配送</dt>
                    <dd>{{ row.logistics_company || '—' }} · {{ row.tracking_no || '暂无运单' }}</dd>
                  </div>
                  <div>
                    <dt>买家备注</dt>
                    <dd>{{ row.buyer_note || '—' }}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="订单号" min-width="155">
          <template #default="{ row }">
            <div class="order-cell">
              <strong>{{ row.order_no }}</strong>
              <span>{{ formatDateTime(row.created_at) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="商品" min-width="200">
          <template #default="{ row }">
            <div class="product-cell">
              <span class="product-icon"><el-icon><Box /></el-icon></span>
              <div>
                <strong>{{ row.items[0]?.product_name || '商品' }}</strong>
                <span v-if="row.items.length > 1">等 {{ row.items.length }} 件商品</span>
                <span v-else>{{ row.items[0]?.sku_spec }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="消费者" min-width="135">
          <template #default="{ row }">
            <div class="customer-cell">
              <span>{{ row.customer_name?.slice(0, 1) || '客' }}</span>
              <div>
                <strong>{{ row.customer_name || '—' }}</strong>
                <small>{{ maskPhone(row.customer_phone || '') }}</small>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="实付金额" width="110" align="right">
          <template #default="{ row }">
            <strong class="amount">{{ formatAmount(row.paid_amount || row.payable_amount) }}</strong>
          </template>
        </el-table-column>

        <el-table-column label="订单状态" width="105" align="center">
          <template #default="{ row }">
            <StatusTag kind="order" :value="row.order_status" dot />
          </template>
        </el-table-column>

        <el-table-column label="售后" width="110">
          <template #default="{ row }">
            <div class="aftersale-cell">
              <span :class="{ 'has-aftersale': row.after_sale_status !== 'none' }">
                {{ afterSaleLabel(row.after_sale_status) }}
              </span>
              <small v-if="row.ticket_count">
                {{ row.ticket_count }} 张工单
              </small>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <div class="table-empty">
            <span><el-icon><Location /></el-icon></span>
            <p>没有找到符合条件的订单</p>
            <small>尝试更换关键词或订单状态。</small>
          </div>
        </template>
      </el-table>

      <div class="table-footer">
        <span>共 {{ result.total }} 笔订单</span>
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
  </div>
</template>

<style scoped>
.platform-page-head {
  margin-bottom: 16px;
}

.order-count {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 12px;
  border: 1px solid #ebe9e7;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
}

.order-count > span {
  display: grid;
  place-items: center;
  width: 29px;
  height: 29px;
  border-radius: 8px;
  color: #db3d2d;
  background: #fff0ed;
  font-size: 14px;
}

.order-count > div {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.order-count strong {
  color: #3f3f46;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
  line-height: 1;
}

.order-count small {
  color: #9d9da5;
  font-size: 8px;
}

.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 12px;
  padding: 13px 15px;
  border-radius: 12px;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 0 0 160px;
}

.filter-field--search {
  flex: 1;
  max-width: 390px;
}

.filter-field label {
  color: #8f8f98;
  font-size: 9px;
}

.filter-field :deep(.el-input__wrapper),
.filter-field :deep(.el-select__wrapper) {
  height: 32px;
  border-radius: 7px;
  box-shadow: 0 0 0 1px #e9e9ee inset;
}

.filter-field :deep(.el-input__inner),
.filter-field :deep(.el-select__placeholder),
.filter-field :deep(.el-select__selected-item) {
  font-size: 10px;
}

.status-select {
  width: 100%;
}

.filter-actions {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 32px;
  border-radius: 7px;
  font-size: 10px;
}

.order-table-card {
  padding: 0;
  overflow: hidden;
  border-radius: 13px;
}

.table-head {
  padding: 13px 16px 11px;
  border-bottom: 1px solid #f3f3f6;
}

.table-head h2 {
  color: #45454d;
  font-size: 12px;
  font-weight: 650;
}

.table-head p {
  margin-top: 3px;
  color: #a5a5ad;
  font-size: 8px;
}

.order-table {
  width: 100%;
  --el-table-header-bg-color: #fbfbfc;
  --el-table-row-hover-bg-color: #fffaf8;
}

.order-table :deep(th.el-table__cell) {
  height: 39px;
  padding: 0;
  border-bottom-color: #f2f2f5;
  color: #9797a0;
  font-size: 9px;
  font-weight: 500;
}

.order-table :deep(td.el-table__cell) {
  padding: 10px 0;
  border-bottom-color: #f5f5f7;
}

.order-table :deep(.el-table__expand-column .cell) {
  padding: 0 0 0 10px;
}

.order-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.order-cell strong {
  color: #5a5a62;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
  font-weight: 600;
}

.order-cell span {
  color: #ababb3;
  font-size: 8px;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.product-icon {
  display: grid;
  place-items: center;
  width: 29px;
  height: 29px;
  border-radius: 7px;
  color: #de4430;
  background: #fff1ee;
  font-size: 13px;
}

.product-cell > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.product-cell strong {
  overflow: hidden;
  color: #5a5a62;
  font-size: 9px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-cell span {
  color: #aaaab2;
  font-size: 8px;
}

.customer-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.customer-cell > span {
  display: grid;
  place-items: center;
  width: 23px;
  height: 23px;
  border-radius: 6px;
  color: #6c7ba7;
  background: #f0f3fa;
  font-size: 8px;
  font-weight: 600;
}

.customer-cell > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-cell strong {
  color: #5c5c65;
  font-size: 9px;
  font-weight: 500;
}

.customer-cell small {
  color: #aaaab2;
  font-size: 8px;
}

.amount {
  color: #d53e2d;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 10px;
  font-weight: 600;
}

.aftersale-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: #b0b0b8;
  font-size: 8px;
}

.aftersale-cell .has-aftersale {
  color: #d96b37;
  font-weight: 500;
}

.expand-panel {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 28px;
  padding: 13px 46px 15px;
  border-top: 1px solid #f7f7f9;
  background: #fcfcfd;
}

.expand-block h4 {
  margin-bottom: 8px;
  color: #8e8e97;
  font-size: 8px;
  font-weight: 650;
  letter-spacing: 0.04em;
}

.expand-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 0;
  border-bottom: 1px dashed #f0f0f3;
}

.expand-item:last-child {
  border-bottom: 0;
}

.expand-item__icon {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  color: #dd4d38;
  background: #fff1ee;
  font-size: 11px;
}

.expand-item__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
}

.expand-item__copy strong {
  color: #64646c;
  font-size: 9px;
  font-weight: 500;
}

.expand-item__copy small {
  color: #ababb3;
  font-size: 8px;
}

.expand-item__price {
  color: #7e7e87;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 9px;
}

.expand-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 18px;
  margin: 0;
}

.expand-info div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.expand-info dt {
  color: #b0b0b8;
  font-size: 8px;
}

.expand-info dd {
  margin: 0;
  color: #73737c;
  font-size: 8px;
  line-height: 1.6;
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
  width: 44px;
  height: 44px;
  border-radius: 13px;
  color: #b3b3bb;
  background: #f6f6f8;
  font-size: 20px;
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
  padding: 11px 15px;
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
  .order-count {
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

  .expand-panel {
    grid-template-columns: 1fr;
    gap: 15px;
    padding: 12px 16px;
  }
}
</style>
