<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, ShoppingBag } from '@element-plus/icons-vue'
import type { Order, Page } from '@/types/api'
import type { Ticket } from '@/types/api'
import { buyerApi } from '@/api/buyer'
import { showError } from '@/api/http'
import { buyerOrderTabs } from '@/utils/labels'
import OrderCard from '@/components/buyer/OrderCard.vue'
import AfterSaleDialog from '@/components/buyer/AfterSaleDialog.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()

const activeTab = ref('all')
const keyword = ref('')
const appliedKeyword = ref('')
const page = ref(1)
const pageSize = 5
const loading = ref(false)
const result = ref<Page<Order>>({
  items: [],
  total: 0,
  page: 1,
  page_size: pageSize,
  counts: {},
})

const dialogVisible = ref(false)
const initialOrderId = ref<number | null>(null)

const tabs = computed(() =>
  buyerOrderTabs.map((tab) => ({
    ...tab,
    count: result.value.counts?.[tab.key] ?? 0,
  })),
)

async function loadOrders(): Promise<void> {
  loading.value = true
  try {
    result.value = await buyerApi.getOrders({
      tab: activeTab.value,
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

function switchTab(key: string): void {
  if (activeTab.value === key) return
  activeTab.value = key
  page.value = 1
  void loadOrders()
}

function search(): void {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
  void loadOrders()
}

function changePage(nextPage: number): void {
  page.value = nextPage
  void loadOrders()
}

function openAfterSale(order?: Order): void {
  initialOrderId.value = order?.id ?? null
  dialogVisible.value = true
}

function handleCreated(ticket: Ticket): void {
  router.push(`/consumer/after-sales/${ticket.id}`)
}

onMounted(loadOrders)
</script>

<template>
  <div class="buyer-orders-page">
    <header class="buyer-page-head">
      <div>
        <p class="eyebrow">MY ORDERS</p>
        <h1>我的订单</h1>
        <p>查看订单状态和物流信息，需要售后时提交问题即可由 AI 先行处理。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openAfterSale()">
        申请售后
      </el-button>
    </header>

    <section class="order-tabs-card">
      <div class="order-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="{ 'is-active': activeTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
          <em v-if="tab.count">{{ tab.count }}</em>
        </button>
      </div>

      <div class="order-search">
        <el-input
          v-model="keyword"
          :prefix-icon="Search"
          placeholder="搜索订单号或商品"
          clearable
          @keyup.enter="search"
          @clear="search"
        />
        <el-button @click="search">搜索</el-button>
      </div>
    </section>

    <section v-loading="loading" class="orders-area">
      <div v-if="result.items.length" class="order-list">
        <OrderCard
          v-for="order in result.items"
          :key="order.id"
          :order="order"
          @after-sale="openAfterSale"
        />
      </div>

      <EmptyState
        v-else-if="!loading"
        title="暂无符合条件的订单"
        description="切换订单状态分类，或者更换搜索条件试试。"
      >
        <el-icon class="empty-bag"><ShoppingBag /></el-icon>
      </EmptyState>

      <div v-if="result.total > pageSize" class="list-pagination">
        <span>共 {{ result.total }} 笔订单</span>
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

    <AfterSaleDialog
      v-model="dialogVisible"
      :initial-order-id="initialOrderId"
      @created="handleCreated"
    />
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
  margin-top: 7px;
  color: #92929c;
  font-size: 12px;
}

.buyer-page-head :deep(.el-button) {
  height: 38px;
  padding: 0 16px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 8px 18px rgba(255, 80, 0, 0.16);
}

.order-tabs-card {
  padding: 0 16px;
  border: 1px solid #ececf1;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 7px 22px rgba(26, 27, 32, 0.035);
}

.order-tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding-top: 8px;
  border-bottom: 1px solid #f3f3f6;
}

.order-tabs button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
  height: 35px;
  padding: 0 11px;
  border-bottom: 2px solid transparent;
  color: #85858f;
  background: transparent;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition:
    color 0.2s ease,
    border-color 0.2s ease;
}

.order-tabs button:hover {
  color: #e9530b;
}

.order-tabs button.is-active {
  color: #eb5207;
  border-bottom-color: #ff5b0d;
  font-weight: 650;
}

.order-tabs em {
  display: grid;
  place-items: center;
  min-width: 15px;
  height: 15px;
  padding: 0 3px;
  border-radius: 4px;
  color: #a0a0a8;
  background: #f5f5f8;
  font-size: 8px;
  font-style: normal;
}

.order-tabs button.is-active em {
  color: #e9530b;
  background: #fff0e7;
}

.order-search {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 430px;
  padding: 10px 0;
}

.order-search :deep(.el-input__wrapper) {
  height: 33px;
  border-radius: 8px;
  background: #fafafb;
  box-shadow: 0 0 0 1px #ececf1 inset;
}

.order-search :deep(.el-input__inner) {
  font-size: 11px;
}

.order-search :deep(.el-button) {
  height: 33px;
  border-radius: 8px;
  font-size: 11px;
}

.orders-area {
  min-height: 330px;
  margin-top: 13px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 17px;
  padding: 2px 3px;
}

.list-pagination > span {
  color: #aaaab2;
  font-size: 10px;
}

.list-pagination :deep(.el-pagination) {
  --el-pagination-button-width: 28px;
  --el-pagination-button-height: 28px;
  font-size: 10px;
}

.list-pagination :deep(.el-pagination.is-background .btn-prev),
.list-pagination :deep(.el-pagination.is-background .btn-next),
.list-pagination :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 7px;
  background: #fff;
  box-shadow: 0 0 0 1px #ececf1 inset;
}

.list-pagination :deep(.el-pagination.is-background .el-pager li.is-active) {
  color: #fff;
  background: #ff5b0d;
  box-shadow: none;
}

.empty-bag {
  font-size: 24px;
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

  .order-tabs-card {
    padding: 0 10px;
  }

  .order-search {
    max-width: none;
  }

  .list-pagination {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
