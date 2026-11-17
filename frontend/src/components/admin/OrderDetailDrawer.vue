<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Box,
  Close,
  CopyDocument,
  Location,
  Plus,
  Tickets,
} from '@element-plus/icons-vue'
import { useAdminUiStore } from '@/stores/adminUi'
import { useMockStore } from '@/stores/mock'
import { formatAmount, formatDateTime, maskPhone } from '@/utils/format'
import { ticketTypeLabel } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const ui = useAdminUiStore()
const mock = useMockStore()

const visible = computed({
  get: () => ui.orderDrawerVisible,
  set: (value: boolean) => {
    ui.orderDrawerVisible = value
  },
})

const order = computed(() =>
  ui.selectedOrderId == null ? undefined : mock.orderById(ui.selectedOrderId),
)

const customer = computed(() =>
  order.value ? mock.customerById(order.value.customerId) : undefined,
)

const tickets = computed(() =>
  order.value ? mock.ticketsForOrder(order.value.id) : [],
)

async function copyOrderNo(): Promise<void> {
  if (!order.value) return
  try {
    await navigator.clipboard.writeText(order.value.orderNo)
    ElMessage.success('订单号已复制')
  } catch {
    ElMessage.error('复制失败，请手动选择订单号')
  }
}

function createTicket(): void {
  if (!order.value) return
  ui.openCreateTicket({
    customerId: order.value.customerId,
    orderId: order.value.id,
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
    <div v-if="order" class="entity-drawer">
      <header class="drawer-head">
        <div>
          <p class="eyebrow">ORDER DETAIL</p>
          <h2>订单详情</h2>
        </div>
        <button class="drawer-close" type="button" @click="visible = false">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <div class="drawer-scroll">
        <section class="product-hero">
          <div class="product-thumb">
            <el-icon><Box /></el-icon>
          </div>
          <div class="product-info">
            <div class="product-status">
              <StatusTag kind="order" :value="order.orderStatus" dot />
              <span>订单号 {{ order.orderNo }}</span>
            </div>
            <h3>{{ order.productName }}</h3>
            <p>{{ order.productSpec }} · 数量 {{ order.quantity }}</p>
          </div>
          <div class="product-amount">
            <span>实付</span>
            <strong>{{ formatAmount(order.amount) }}</strong>
          </div>
        </section>

        <section class="detail-section">
          <div class="detail-section__head">
            <h3>订单信息</h3>
            <button class="inline-action" type="button" @click="copyOrderNo">
              <el-icon><CopyDocument /></el-icon>
              复制订单号
            </button>
          </div>
          <dl class="info-grid">
            <div>
              <dt>下单时间</dt>
              <dd>{{ formatDateTime(order.createdAt) }}</dd>
            </div>
            <div>
              <dt>最近更新</dt>
              <dd>{{ formatDateTime(order.updatedAt) }}</dd>
            </div>
            <div>
              <dt>客户</dt>
              <dd>{{ customer?.name || '—' }}</dd>
            </div>
            <div>
              <dt>联系电话</dt>
              <dd>{{ customer ? maskPhone(customer.phone) : '—' }}</dd>
            </div>
          </dl>
        </section>

        <section class="detail-section">
          <div class="detail-section__head">
            <h3>物流信息</h3>
            <span class="logistics-company">
              <el-icon><Location /></el-icon>
              {{ order.logisticsCompany }}
            </span>
          </div>
          <div class="logistics-card">
            <div class="logistics-line">
              <span class="logistics-node is-done" />
              <span class="logistics-track" />
              <span
                class="logistics-node"
                :class="{ 'is-done': order.orderStatus !== 'pending_shipment' }"
              />
              <span class="logistics-track" />
              <span
                class="logistics-node"
                :class="{
                  'is-done': ['received', 'completed'].includes(order.orderStatus),
                }"
              />
            </div>
            <div class="logistics-labels">
              <span>已下单</span>
              <span>已发货</span>
              <span>已签收</span>
            </div>
            <div class="tracking-row">
              <span>物流单号</span>
              <strong>{{ order.trackingNo }}</strong>
            </div>
          </div>
        </section>

        <section class="detail-section">
          <div class="detail-section__head">
            <h3>
              售后工单
              <span class="section-count">{{ tickets.length }}</span>
            </h3>
            <button class="inline-action is-accent" type="button" @click="createTicket">
              <el-icon><Plus /></el-icon>
              创建工单
            </button>
          </div>

          <div v-if="tickets.length" class="ticket-list">
            <button
              v-for="ticket in tickets"
              :key="ticket.id"
              class="ticket-row"
              type="button"
              @click="ui.openTicketDrawer(ticket.id)"
            >
              <span class="ticket-row__icon">
                <el-icon><Tickets /></el-icon>
              </span>
              <span class="ticket-row__copy">
                <span class="ticket-row__title">
                  {{ ticketTypeLabel(ticket.type) }}
                  <small>{{ ticket.ticketNo }}</small>
                </span>
                <span>{{ ticket.description }}</span>
              </span>
              <span class="ticket-row__tags">
                <StatusTag kind="priority" :value="ticket.priority" />
                <StatusTag kind="ticket" :value="ticket.status" />
              </span>
            </button>
          </div>
          <EmptyState
            v-else
            compact
            title="暂无售后工单"
            description="如有售后问题，可基于当前订单创建工单。"
          >
            <el-button size="small" type="primary" :icon="Plus" @click="createTicket">
              创建工单
            </el-button>
          </EmptyState>
        </section>
      </div>

      <footer class="drawer-foot">
        <el-button :icon="CopyDocument" @click="copyOrderNo">复制订单号</el-button>
        <el-button type="primary" :icon="Plus" @click="createTicket">
          创建售后工单
        </el-button>
      </footer>
    </div>

    <EmptyState
      v-else
      title="未找到订单"
      description="该订单可能已被删除或演示数据已重置。"
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
  align-items: center;
  justify-content: space-between;
  flex: 0 0 auto;
  padding: 22px 24px 18px;
  border-bottom: 1px solid #ececf1;
  background: #fff;
}

.drawer-head h2 {
  margin-top: 4px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-strong);
}

.drawer-close {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #96969f;
  background: #f6f6f8;
  font-size: 16px;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.drawer-close:hover {
  color: #3d3d42;
  background: #eeeeF2;
}

.drawer-scroll {
  flex: 1;
  min-height: 0;
  padding: 18px 20px 26px;
  overflow-y: auto;
}

.product-hero {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  padding: 16px;
  border: 1px solid #ececf1;
  border-radius: 14px;
  background: #fff;
}

.product-thumb {
  display: grid;
  place-items: center;
  flex: 0 0 58px;
  width: 58px;
  height: 58px;
  border-radius: 12px;
  color: #ff6c25;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.4), transparent),
    #fff2e9;
  font-size: 27px;
}

.product-info {
  min-width: 0;
  flex: 1;
}

.product-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a0a0aa;
  font-size: 10px;
}

.product-info h3 {
  margin-top: 7px;
  overflow: hidden;
  color: #333339;
  font-size: 14px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-info p {
  margin-top: 5px;
  color: #9a9aa3;
  font-size: 11px;
}

.product-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex: 0 0 auto;
  gap: 4px;
}

.product-amount span {
  color: #a3a3ab;
  font-size: 10px;
}

.product-amount strong {
  color: #df3b28;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 18px;
  font-weight: 700;
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
  margin-bottom: 14px;
}

.detail-section__head h3 {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #3a3a40;
  font-size: 12px;
  font-weight: 650;
}

.section-count {
  display: inline-grid;
  place-items: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 5px;
  color: #a0a0aa;
  background: #f5f5f7;
  font-size: 9px;
}

.inline-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  color: #93939c;
  background: transparent;
  font-size: 10px;
  cursor: pointer;
}

.inline-action:hover {
  color: var(--brand);
}

.inline-action.is-accent {
  color: var(--brand);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 16px;
  margin: 0;
}

.info-grid dt {
  color: #a3a3ac;
  font-size: 10px;
}

.info-grid dd {
  margin: 4px 0 0;
  color: #4f4f58;
  font-size: 12px;
}

.logistics-company {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #96969f;
  font-size: 10px;
}

.logistics-card {
  padding: 13px;
  border-radius: 10px;
  background: #fafafb;
}

.logistics-line {
  display: flex;
  align-items: center;
  padding: 0 11px;
}

.logistics-node {
  flex: 0 0 7px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #dcdce3;
}

.logistics-node.is-done {
  background: var(--brand);
  box-shadow: 0 0 0 3px rgba(255, 80, 0, 0.1);
}

.logistics-track {
  flex: 1;
  height: 1px;
  background: #e7e7ed;
}

.logistics-node.is-done + .logistics-track {
  background: #ffd3bc;
}

.logistics-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  color: #a6a6af;
  font-size: 9px;
}

.tracking-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 13px;
  padding-top: 11px;
  border-top: 1px dashed #e8e8ee;
  font-size: 10px;
}

.tracking-row span {
  color: #a3a3ac;
}

.tracking-row strong {
  color: #60606a;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ticket-row {
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

.ticket-row:hover {
  border-color: #ffdbc8;
  background: #fffaf7;
}

.ticket-row__icon {
  display: grid;
  place-items: center;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #ee7238;
  background: #fff4ed;
  font-size: 15px;
}

.ticket-row__copy {
  min-width: 0;
  flex: 1;
}

.ticket-row__title {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #4e4e57;
  font-size: 11px;
  font-weight: 600;
}

.ticket-row__title small {
  color: #b0b0b8;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 9px;
  font-weight: 400;
}

.ticket-row__copy > span:last-child {
  display: block;
  margin-top: 3px;
  overflow: hidden;
  color: #a3a3ac;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ticket-row__tags {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex: 0 0 auto;
}

.ticket-row__tags :deep(.status-tag) {
  height: 18px;
  padding: 0 6px;
  font-size: 9px;
}

.drawer-foot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex: 0 0 auto;
  padding: 13px 20px;
  border-top: 1px solid #ececf1;
  background: #fff;
}

@media (max-width: 640px) {
  .product-hero {
    flex-wrap: wrap;
  }

  .product-amount {
    width: 100%;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding-top: 10px;
    border-top: 1px dashed #eeeef3;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .drawer-foot {
    padding: 12px;
  }
}
</style>
