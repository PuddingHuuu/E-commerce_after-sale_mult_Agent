<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Box, MagicStick, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Order, Ticket } from '@/types/api'
import { buyerApi } from '@/api/buyer'
import { showError } from '@/api/http'
import { afterSaleEligibleStatuses } from '@/utils/labels'
import { formatAmount } from '@/utils/format'
import StatusTag from '@/components/common/StatusTag.vue'

const props = defineProps<{
  modelValue: boolean
  initialOrderId?: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: [ticket: Ticket]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const loadingOrders = ref(false)
const submitting = ref(false)
const orders = ref<Order[]>([])
const form = reactive({
  order_id: null as number | null,
  description: '',
  expected_resolution: '',
})

const eligibleOrders = computed(() =>
  orders.value.filter((order) => afterSaleEligibleStatuses.has(order.order_status)),
)
const selectedOrder = computed(() => orders.value.find((order) => order.id === form.order_id))

async function loadOrders(): Promise<void> {
  loadingOrders.value = true
  try {
    const page = await buyerApi.getOrders({ tab: 'all', page: 1, page_size: 50 })
    orders.value = page.items
    if (props.initialOrderId && eligibleOrders.value.some((order) => order.id === props.initialOrderId)) {
      form.order_id = props.initialOrderId
    } else if (!form.order_id) {
      form.order_id = eligibleOrders.value[0]?.id ?? null
    }
  } catch (error) {
    showError(error)
  } finally {
    loadingOrders.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    form.description = ''
    form.expected_resolution = ''
    form.order_id = props.initialOrderId ?? null
    void loadOrders()
  },
)

async function submit(): Promise<void> {
  if (!form.order_id) {
    ElMessage.warning('请选择关联订单')
    return
  }
  if (form.description.trim().length < 10) {
    ElMessage.warning('请至少用 10 个字描述问题')
    return
  }
  submitting.value = true
  try {
    const ticket = await buyerApi.createTicket({
      order_id: form.order_id,
      description: form.description.trim(),
      expected_resolution: form.expected_resolution.trim() || null,
    })
    ElMessage.success('售后申请已提交，AI 正在处理')
    visible.value = false
    emit('created', ticket)
  } catch (error) {
    showError(error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="570px"
    :close-on-click-modal="false"
    append-to-body
  >
    <template #header>
      <div class="dialog-head">
        <span class="dialog-head__icon"><el-icon><MagicStick /></el-icon></span>
        <div>
          <h2>申请售后</h2>
          <p>请提交完整问题信息，AI 会先核对订单并生成处理建议。</p>
        </div>
      </div>
    </template>

    <div class="dialog-tip">
      <span><el-icon><MagicStick /></el-icon></span>
      <p>
        AI 处理完成后，如果结果没有解决您的问题，可以在售后详情中点击「不满意，转人工」，
        之后才会开放人工聊天窗口。
      </p>
    </div>

    <el-form label-position="top" class="after-sale-form">
      <el-form-item label="关联订单" required>
        <el-select
          v-model="form.order_id"
          class="full-width"
          :loading="loadingOrders"
          filterable
          placeholder="请选择需要售后的订单"
        >
          <el-option
            v-for="order in eligibleOrders"
            :key="order.id"
            :value="order.id"
            :label="`${order.order_no} · ${order.items[0]?.product_name || '订单商品'}`"
          >
            <div class="order-option">
              <span class="order-option__icon"><el-icon><Box /></el-icon></span>
              <span class="order-option__copy">
                <strong>{{ order.items[0]?.product_name || '订单商品' }}</strong>
                <small>{{ order.order_no }} · {{ formatAmount(order.payable_amount) }}</small>
              </span>
              <StatusTag kind="order" :value="order.order_status" />
            </div>
          </el-option>
        </el-select>
        <p v-if="!loadingOrders && eligibleOrders.length === 0" class="warning">
          当前没有可申请售后的订单。
        </p>
      </el-form-item>

      <el-form-item label="问题描述" required>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="5"
          maxlength="1200"
          show-word-limit
          placeholder="请描述商品问题、发生时间、当前状态和期望的处理方式，至少 10 个字"
        />
      </el-form-item>

      <el-form-item label="期望处理方式（选填）">
        <el-input
          v-model="form.expected_resolution"
          maxlength="200"
          placeholder="例如：退货退款、换货、维修"
        />
      </el-form-item>
    </el-form>

    <p v-if="selectedOrder" class="selected-note">
      当前选择：{{ selectedOrder.order_no }} · {{ formatAmount(selectedOrder.payable_amount) }}
    </p>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :loading="submitting"
        :disabled="eligibleOrders.length === 0"
        :icon="Plus"
        @click="submit"
      >
        提交售后申请
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-head {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.dialog-head__icon {
  display: grid;
  place-items: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  color: #eb5a16;
  background: #fff2e9;
  font-size: 20px;
}

.dialog-head h2 {
  color: #2e2e34;
  font-size: 18px;
  font-weight: 700;
}

.dialog-head p {
  margin-top: 4px;
  color: #9b9ba4;
  font-size: 10px;
}

.dialog-tip {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin-bottom: 16px;
  padding: 10px 11px;
  border: 1px solid #ffe3d5;
  border-radius: 9px;
  color: #946e59;
  background: #fffaf6;
}

.dialog-tip > span {
  margin-top: 1px;
  color: #eb6a2b;
}

.dialog-tip p {
  font-size: 9px;
  line-height: 1.75;
}

.after-sale-form :deep(.el-form-item__label) {
  padding-bottom: 5px;
  color: #6f6f78;
  font-size: 10px;
}

.after-sale-form :deep(.el-form-item) {
  margin-bottom: 15px;
}

.full-width {
  width: 100%;
}

.order-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
}

.order-option__icon {
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 7px;
  color: #e4612a;
  background: #fff3ec;
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
  color: #505058;
  font-size: 10px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-option__copy small {
  color: #a4a4ac;
  font-size: 8px;
}

.warning {
  margin-top: 5px;
  color: #c2861a;
  font-size: 9px;
}

.selected-note {
  padding: 8px 10px;
  border-radius: 7px;
  color: #9c9ca5;
  background: #f8f8fa;
  font-size: 9px;
}

@media (max-width: 620px) {
  .dialog-tip {
    margin-top: 4px;
  }
}
</style>
