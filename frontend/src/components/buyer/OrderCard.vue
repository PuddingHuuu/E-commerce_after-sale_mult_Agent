<script setup lang="ts">
import { computed } from 'vue'
import { Box, Location, Tickets } from '@element-plus/icons-vue'
import type { Order } from '@/types/api'
import { afterSaleEligibleStatuses, orderSourceLabels, paymentMethodLabels } from '@/utils/labels'
import { formatAmount, formatDateTime } from '@/utils/format'
import StatusTag from '@/components/common/StatusTag.vue'

const props = defineProps<{
  order: Order
}>()

const emit = defineEmits<{
  afterSale: [order: Order]
}>()

const canApplyAfterSale = computed(() => afterSaleEligibleStatuses.has(props.order.order_status))
const totalQuantity = computed(() => props.order.items.reduce((sum, item) => sum + item.quantity, 0))
const sourceLabel = computed(() => orderSourceLabels[props.order.order_source] || props.order.order_source)
const paymentLabel = computed(() =>
  props.order.payment_method ? paymentMethodLabels[props.order.payment_method] || props.order.payment_method : '未支付',
)

function applyAfterSale(): void {
  if (!canApplyAfterSale.value) return
  emit('afterSale', props.order)
}
</script>

<template>
  <article class="order-card">
    <header class="order-card__head">
      <div class="order-card__identity">
        <span class="order-card__icon"><el-icon><Box /></el-icon></span>
        <div>
          <div class="order-card__no-line">
            <span>订单号 {{ order.order_no }}</span>
            <StatusTag kind="order" :value="order.order_status" dot />
          </div>
          <p>{{ formatDateTime(order.created_at) }} · {{ sourceLabel }} · {{ paymentLabel }}</p>
        </div>
      </div>
      <div class="order-card__total">
        <span>实付</span>
        <strong>{{ formatAmount(order.paid_amount || order.payable_amount) }}</strong>
      </div>
    </header>

    <div class="order-card__items">
      <div v-for="item in order.items" :key="item.id" class="order-product">
        <span class="order-product__thumb"><el-icon><Box /></el-icon></span>
        <div class="order-product__copy">
          <strong>{{ item.product_name }}</strong>
          <span>{{ item.sku_spec || '默认规格' }}</span>
        </div>
        <div class="order-product__price">
          <span>× {{ item.quantity }}</span>
          <strong>{{ formatAmount(item.pay_amount) }}</strong>
        </div>
      </div>
    </div>

    <div class="order-card__meta">
      <span>
        <el-icon><Location /></el-icon>
        {{ order.logistics_company || '暂无物流信息' }}
        <template v-if="order.tracking_no"> · {{ order.tracking_no }}</template>
      </span>
      <span>共 {{ totalQuantity }} 件商品</span>
      <span class="order-card__amount-line">
        商品 {{ formatAmount(order.goods_amount) }}
        <template v-if="Number(order.discount_amount) > 0">
          · 优惠 {{ formatAmount(order.discount_amount) }}
        </template>
        <template v-if="Number(order.freight_amount) > 0">
          · 运费 {{ formatAmount(order.freight_amount) }}
        </template>
      </span>
    </div>

    <footer class="order-card__foot">
      <span v-if="order.after_sale_status !== 'none'" class="order-aftersale-hint">
        <el-icon><Tickets /></el-icon>
        {{ order.after_sale_status === 'completed' ? '售后已完成' : '售后处理中' }}
      </span>
      <span v-else class="order-aftersale-hint is-muted">
        售后入口：提交后由 AI 先处理
      </span>
      <el-tooltip
        :disabled="canApplyAfterSale"
        content="当前订单状态暂不支持申请售后"
        placement="top"
      >
        <span>
          <el-button
            type="primary"
            plain
            size="small"
            :disabled="!canApplyAfterSale"
            @click="applyAfterSale"
          >
            申请售后
          </el-button>
        </span>
      </el-tooltip>
    </footer>
  </article>
</template>

<style scoped>
.order-card {
  overflow: hidden;
  border: 1px solid #ececf1;
  border-radius: 15px;
  background: #fff;
  box-shadow: 0 7px 24px rgba(28, 29, 35, 0.035);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.order-card:hover {
  border-color: #e7d8ce;
  box-shadow: 0 11px 30px rgba(28, 29, 35, 0.06);
}

.order-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 17px;
  border-bottom: 1px solid #f3f3f6;
  background: linear-gradient(180deg, #fbf9f6, #fff);
}

.order-card__identity {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.order-card__icon {
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: #a8755f;
  background: #f7f1ec;
  font-size: 15px;
}

.order-card__no-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
  color: #57575f;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 13px;
  font-weight: 600;
}

.order-card__identity p {
  margin-top: 4px;
  color: #a3a3ac;
  font-size: 12px;
}

.order-card__total {
  display: flex;
  align-items: baseline;
  gap: 5px;
  flex: 0 0 auto;
}

.order-card__total span {
  color: #a4a4ac;
  font-size: 12px;
}

.order-card__total strong {
  color: #a85f52;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 17px;
  font-weight: 700;
}

.order-card__items {
  padding: 7px 17px;
}

.order-product {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px dashed #f2f2f5;
}

.order-product:last-child {
  border-bottom: 0;
}

.order-product__thumb {
  display: grid;
  place-items: center;
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  border-radius: 11px;
  color: #a8755f;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.55), transparent),
    #f7f1ec;
  font-size: 19px;
}

.order-product__copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.order-product__copy strong {
  overflow: hidden;
  color: #45454c;
  font-size: 13px;
  font-weight: 550;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-product__copy span {
  color: #a1a1aa;
  font-size: 12px;
}

.order-product__price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  flex: 0 0 auto;
}

.order-product__price span {
  color: #a2a2aa;
  font-size: 12px;
}

.order-product__price strong {
  color: #66666f;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 13px;
  font-weight: 500;
}

.order-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px 16px;
  padding: 10px 17px;
  border-top: 1px solid #f5f5f7;
  color: #9b9ba4;
  background: #fbfbfc;
  font-size: 12px;
}

.order-card__meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.order-card__amount-line {
  margin-left: auto;
}

.order-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 11px 17px;
  border-top: 1px solid #f3f3f6;
}

.order-aftersale-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #8c6a57;
  font-size: 12px;
}

.order-aftersale-hint.is-muted {
  color: #b2b2ba;
}

.order-card__foot :deep(.el-button) {
  height: 34px;
  padding: 0 16px;
  border-color: #e7d8ce;
  border-radius: 8px;
  color: #99664f;
  background: #faf6f2;
  font-size: 13px;
}

.order-card__foot :deep(.el-button:hover) {
  border-color: #c9a58f;
  color: #80523f;
  background: #f7f1ec;
}

@media (max-width: 660px) {
  .order-card__head,
  .order-card__meta,
  .order-card__foot {
    padding-right: 13px;
    padding-left: 13px;
  }

  .order-card__items {
    padding-right: 13px;
    padding-left: 13px;
  }

  .order-card__meta {
    gap: 6px 10px;
  }

  .order-card__amount-line {
    width: 100%;
    margin-left: 0;
  }

  .order-card__total strong {
    font-size: 15px;
  }
}
</style>
