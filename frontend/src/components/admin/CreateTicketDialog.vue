<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Close, Plus, Tickets } from '@element-plus/icons-vue'
import { useAdminUiStore } from '@/stores/adminUi'
import { useMockStore } from '@/stores/mock'
import type { TicketPriority, TicketType } from '@/types'
import { formatAmount, initials, maskPhone } from '@/utils/format'
import {
  priorityOptions,
  ticketTypeLabel,
  ticketTypeOptions,
} from '@/utils/labels'

const ui = useAdminUiStore()
const mock = useMockStore()

const visible = computed({
  get: () => ui.ticketDialog.visible,
  set: (value: boolean) => {
    ui.ticketDialog.visible = value
  },
})

const customerId = computed(() => {
  if (ui.ticketDialog.customerId != null) return ui.ticketDialog.customerId
  if (ui.ticketDialog.orderId != null) {
    return mock.orderById(ui.ticketDialog.orderId)?.customerId ?? null
  }
  return null
})

const customer = computed(() =>
  customerId.value == null ? undefined : mock.customerById(customerId.value),
)

const customerOrders = computed(() =>
  customerId.value == null ? [] : mock.ordersForCustomer(customerId.value),
)

const form = reactive({
  orderId: null as number | null,
  type: 'refund_only' as TicketType,
  priority: 'normal' as TicketPriority,
  description: '',
})

const selectedOrder = computed(() =>
  form.orderId == null ? undefined : mock.orderById(form.orderId),
)

watch(
  () => ui.ticketDialog.visible,
  (open) => {
    if (!open) return
    form.orderId = ui.ticketDialog.orderId ?? customerOrders.value[0]?.id ?? null
    form.type = 'refund_only'
    form.priority = 'normal'
    form.description = ''
  },
)

function resetForm(): void {
  form.orderId = null
  form.type = 'refund_only'
  form.priority = 'normal'
  form.description = ''
}

function submit(): void {
  if (!form.orderId) {
    ElMessage.warning('请选择关联订单')
    return
  }
  if (!form.description.trim()) {
    ElMessage.warning('请填写问题描述')
    return
  }

  try {
    const ticket = mock.createTicket({
      orderId: form.orderId,
      conversationId: ui.ticketDialog.conversationId,
      type: form.type,
      priority: form.priority,
      description: form.description,
    })
    visible.value = false
    resetForm()
    ElMessage.success(`工单 ${ticket.ticketNo} 已创建`)
    ui.openTicketDrawer(ticket.id)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建工单失败')
  }
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="590px"
    class="ticket-dialog"
    :close-on-click-modal="false"
    append-to-body
    @closed="resetForm"
  >
    <template #header>
      <div class="dialog-head">
        <span class="dialog-head__icon">
          <el-icon><Tickets /></el-icon>
        </span>
        <div>
          <h2>创建售后工单</h2>
          <p>将客户问题登记为工单，后续可在工单中心持续跟进。</p>
        </div>
      </div>
    </template>

    <div v-if="customer" class="customer-strip">
      <span class="customer-avatar">{{ initials(customer.name) }}</span>
      <div>
        <strong>{{ customer.name }}</strong>
        <span>{{ maskPhone(customer.phone) }}</span>
      </div>
      <span class="customer-strip__label">当前客户</span>
    </div>

    <el-form label-position="top" class="ticket-form">
      <el-form-item label="关联订单" required>
        <el-select
          v-model="form.orderId"
          placeholder="请选择需要售后的订单"
          class="full-width"
        >
          <el-option
            v-for="order in customerOrders"
            :key="order.id"
            :value="order.id"
            :label="`${order.orderNo} · ${order.productName}`"
          >
            <div class="order-option">
              <span class="order-option__icon">
                <el-icon><Box /></el-icon>
              </span>
              <span class="order-option__copy">
                <strong>{{ order.productName }}</strong>
                <span>{{ order.orderNo }} · {{ order.productSpec }}</span>
              </span>
              <span class="order-option__amount">{{ formatAmount(order.amount) }}</span>
            </div>
          </el-option>
        </el-select>
        <p v-if="customerOrders.length === 0" class="form-warning">
          当前客户暂无可关联订单，暂时无法创建售后工单。
        </p>
      </el-form-item>

      <div class="form-row">
        <el-form-item label="工单类型" required>
          <el-select v-model="form.type" class="full-width">
            <el-option
              v-for="option in ticketTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select v-model="form.priority" class="full-width">
            <el-option
              v-for="option in priorityOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="问题描述" required>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          maxlength="500"
          show-word-limit
          :placeholder="
            selectedOrder
              ? `请描述「${selectedOrder.productName}」的售后问题和客户诉求…`
              : '请描述客户遇到的问题和期望的处理方式…'
          "
        />
      </el-form-item>
    </el-form>

    <div class="dialog-note">
      <span>
        工单创建后状态默认为「待处理」，当前处理人为
        <strong>客服小橙</strong>。你可以随时在工单中心更新状态。
      </span>
      <span class="dialog-note__type">{{ ticketTypeLabel(form.type) }}</span>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button
          type="primary"
          :icon="Plus"
          :disabled="customerOrders.length === 0"
          @click="submit"
        >
          创建工单
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-right: 22px;
}

.dialog-head__icon {
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  color: #df2f21;
  background: linear-gradient(145deg, #fff1ee, #ffe4df);
  font-size: 20px;
}

.dialog-head h2 {
  color: #242429;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.dialog-head p {
  margin-top: 4px;
  color: #96969f;
  font-size: 11px;
  line-height: 1.55;
}

.customer-strip {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 18px;
  padding: 10px 12px;
  border: 1px solid #f0f0f4;
  border-radius: 10px;
  background: #fafafb;
}

.customer-avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  color: #fff;
  background: linear-gradient(145deg, #ff8e58, #e33724);
  font-size: 11px;
  font-weight: 700;
}

.customer-strip > div {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.customer-strip strong {
  color: #4f4f58;
  font-size: 11px;
  font-weight: 600;
}

.customer-strip div span {
  color: #a0a0a9;
  font-size: 9px;
}

.customer-strip__label {
  margin-left: auto;
  padding: 3px 7px;
  border-radius: 4px;
  color: #96969f;
  background: #f0f0f4;
  font-size: 9px;
}

.ticket-form :deep(.el-form-item__label) {
  padding-bottom: 5px;
  color: #6d6d76;
  font-size: 11px;
  font-weight: 500;
}

.ticket-form :deep(.el-form-item) {
  margin-bottom: 17px;
}

.full-width {
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.order-option {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 3px 0;
}

.order-option__icon {
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 7px;
  color: #e55331;
  background: #fff3ed;
  font-size: 13px;
}

.order-option__copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}

.order-option__copy strong {
  overflow: hidden;
  color: #4b4b53;
  font-size: 11px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-option__copy span {
  color: #a5a5ad;
  font-size: 9px;
}

.order-option__amount {
  color: #d4382b;
  font-size: 10px;
}

.form-warning {
  margin-top: 6px;
  color: #d88600;
  font-size: 10px;
}

.dialog-note {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #93939d;
  background: #f8f8fa;
  font-size: 10px;
  line-height: 1.6;
}

.dialog-note strong {
  color: #60606a;
  font-weight: 500;
}

.dialog-note__type {
  flex: 0 0 auto;
  padding: 3px 7px;
  border: 1px solid #ffddcb;
  border-radius: 4px;
  color: #e15b2c;
  background: #fff8f3;
  font-size: 9px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .dialog-note {
    align-items: flex-start;
  }
}
</style>
