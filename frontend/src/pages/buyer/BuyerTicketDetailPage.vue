<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Box,
  ChatDotRound,
  Check,
  Clock,
  Headset,
  MagicStick,
  Warning,
} from '@element-plus/icons-vue'
import type { Ticket } from '@/types/api'
import { buyerApi } from '@/api/buyer'
import { getErrorMessage, showError } from '@/api/http'
import {
  formatAmount,
  formatDateTime,
  fromNow,
} from '@/utils/format'
import { ticketCategoryLabel } from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const router = useRouter()

const ticket = ref<Ticket | null>(null)
const loading = ref(true)
const submittingFeedback = ref(false)
const loadError = ref('')
let timer: number | null = null

const ticketId = computed(() => Number(route.params.id))

const canFeedback = computed(() => ticket.value?.status === 'awaiting_feedback')
const hasConversation = computed(() => Boolean(ticket.value?.conversation_id))
const isClosed = computed(() =>
  ['resolved', 'closed'].includes(ticket.value?.status || ''),
)
const isAiProcessing = computed(() => ticket.value?.status === 'ai_processing')
const hasHumanStage = computed(() =>
  Boolean(
    ticket.value?.conversation_id ||
      ['waiting_human', 'human_processing'].includes(ticket.value?.status || ''),
  ),
)

const progressSteps = computed(() => {
  const status = ticket.value?.status || ''
  const steps = [
    { key: 'submitted', label: '提交申请', active: false, done: true },
    {
      key: 'ai',
      label: 'AI 处理',
      active: status === 'ai_processing',
      done: status !== 'ai_processing',
    },
    {
      key: 'feedback',
      label: '结果确认',
      active: status === 'awaiting_feedback',
      done: ['waiting_human', 'human_processing', 'resolved', 'closed'].includes(status),
    },
  ]
  if (hasHumanStage.value) {
    steps.push({
      key: 'human',
      label: '人工处理',
      active: ['waiting_human', 'human_processing'].includes(status),
      done: ['resolved', 'closed'].includes(status),
    })
  }
  steps.push({
    key: 'done',
    label: '处理完成',
    active: false,
    done: ['resolved', 'closed'].includes(status),
  })
  return steps
})

const statusTitle = computed(() => {
  const status = ticket.value?.status
  if (status === 'ai_processing') return 'AI 正在处理您的售后申请'
  if (status === 'awaiting_feedback') return 'AI 已生成处理建议，请确认结果'
  if (status === 'waiting_human') return '已转人工，正在等待平台客服接入'
  if (status === 'human_processing') return '平台客服正在处理您的问题'
  if (status === 'resolved') return '售后问题已解决'
  if (status === 'closed') return '售后流程已结束'
  return '售后处理详情'
})

const statusDescription = computed(() => {
  const status = ticket.value?.status
  if (status === 'ai_processing') {
    return '系统正在依次执行分类、数据检索和回复生成，通常只需要几秒钟。'
  }
  if (status === 'awaiting_feedback') {
    return '如果 AI 的建议解决了您的问题，请点击已解决；如果仍有疑问，可以转人工继续沟通。'
  }
  if (status === 'waiting_human') {
    return 'AI 已停止处理，平台客服接入后即可在对话框内继续沟通。'
  }
  if (status === 'human_processing') {
    return '平台客服已经接入会话，您可以在对话框中继续补充问题。'
  }
  return '本次售后申请已完成，您可以返回售后服务列表查看其他记录。'
})

async function loadTicket(silent = false): Promise<void> {
  if (!Number.isFinite(ticketId.value)) {
    loadError.value = '售后单不存在'
    loading.value = false
    return
  }
  if (!silent) loading.value = true
  try {
    ticket.value = await buyerApi.getTicket(ticketId.value)
    loadError.value = ''
  } catch (error) {
    loadError.value = getErrorMessage(error)
    if (!silent) showError(error)
  } finally {
    loading.value = false
    setupPolling()
  }
}

function setupPolling(): void {
  if (timer) {
    window.clearInterval(timer)
    timer = null
  }
  if (!ticket.value) return
  if (['ai_processing', 'waiting_human'].includes(ticket.value.status)) {
    timer = window.setInterval(() => void loadTicket(true), 1800)
  }
}

async function confirmSatisfied(): Promise<void> {
  if (!ticket.value || submittingFeedback.value) return
  try {
    await ElMessageBox.confirm(
      '确认问题已经解决后，本次售后申请将结束。',
      '确认问题已解决',
      {
        confirmButtonText: '已解决',
        cancelButtonText: '再想想',
        type: 'success',
      },
    )
  } catch {
    return
  }

  submittingFeedback.value = true
  try {
    const result = await buyerApi.feedback(ticket.value.id, { satisfied: true })
    ticket.value = result.ticket
    ElMessage.success('已确认解决，本次售后已完成')
    setupPolling()
  } catch (error) {
    showError(error)
  } finally {
    submittingFeedback.value = false
  }
}

async function requestHuman(): Promise<void> {
  if (!ticket.value || submittingFeedback.value) return
  let reason = ''
  try {
    const result = await ElMessageBox.prompt(
      '可以简单说明 AI 处理结果为什么没有解决您的问题，平台客服会继续跟进。',
      '转人工处理',
      {
        confirmButtonText: '转人工',
        cancelButtonText: '取消',
        inputPlaceholder: '选填，例如：物流一直没有更新',
        inputType: 'textarea',
        inputValidator: () => true,
      },
    )
    reason = result.value || ''
  } catch {
    return
  }

  submittingFeedback.value = true
  try {
    const result = await buyerApi.feedback(ticket.value.id, {
      satisfied: false,
      reason: reason || '用户对 AI 处理结果不满意',
    })
    ticket.value = result.ticket
    ElMessage.success('已为您转接人工客服')
    if (result.conversation_id) {
      await router.push({
        path: '/consumer/chat',
        query: { conversation: String(result.conversation_id) },
      })
    } else {
      setupPolling()
    }
  } catch (error) {
    showError(error)
  } finally {
    submittingFeedback.value = false
  }
}

function enterConversation(): void {
  if (!ticket.value?.conversation_id) return
  router.push({
    path: '/consumer/chat',
    query: { conversation: String(ticket.value.conversation_id) },
  })
}

onMounted(() => void loadTicket())

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="ticket-detail-page">
    <button class="back-link" type="button" @click="router.push('/consumer/after-sales')">
      <el-icon><ArrowLeft /></el-icon>
      返回售后服务
    </button>

    <div v-loading="loading" class="detail-layout">
      <template v-if="ticket">
        <main class="detail-main">
          <section class="ticket-hero" :class="`status-${ticket.status}`">
            <div class="ticket-hero__top">
              <div>
                <p class="eyebrow">AFTER-SALE DETAIL</p>
                <div class="ticket-hero__title">
                  <h1>{{ ticket.subject }}</h1>
                  <StatusTag kind="ticket" :value="ticket.status" dot />
                </div>
                <p class="ticket-hero__meta">
                  售后单号 {{ ticket.ticket_no }}
                  <span>·</span>
                  提交于 {{ formatDateTime(ticket.created_at) }}
                </p>
              </div>
              <span class="ticket-hero__icon">
                <el-icon><MagicStick /></el-icon>
              </span>
            </div>

            <div class="status-copy">
              <span class="status-copy__dot" />
              <div>
                <strong>{{ statusTitle }}</strong>
                <p>{{ statusDescription }}</p>
              </div>
            </div>

            <div class="progress-track">
              <div
                v-for="(step, index) in progressSteps"
                :key="step.key"
                class="progress-step"
                :class="{ 'is-done': step.done, 'is-active': step.active }"
              >
                <div class="progress-step__line" v-if="index > 0" />
                <span class="progress-step__dot">
                  <el-icon v-if="step.done"><Check /></el-icon>
                  <template v-else>{{ index + 1 }}</template>
                </span>
                <span>{{ step.label }}</span>
              </div>
            </div>
          </section>

          <section v-if="isAiProcessing" class="processing-card surface-card">
            <div class="ai-loader"><span /><span /><span /></div>
            <div>
              <strong>AI 正在处理</strong>
              <p>正在执行分类 → 数据检索 → 生成方案，请稍候…</p>
            </div>
          </section>

          <section v-if="ticket.ai_reply" class="ai-result-card surface-card">
            <div class="section-heading">
              <div>
                <span class="section-icon"><el-icon><MagicStick /></el-icon></span>
                <div>
                  <p class="eyebrow">AI RESULT</p>
                  <h2>AI 处理建议</h2>
                </div>
              </div>
              <span v-if="ticket.category" class="category-chip">
                {{ ticketCategoryLabel(ticket.category) }}
              </span>
            </div>

            <div class="ai-answer">{{ ticket.ai_reply }}</div>

            <div v-if="ticket.ai_result_json?.steps?.length" class="suggestion-steps">
              <span>建议步骤</span>
              <ol>
                <li v-for="step in ticket.ai_result_json.steps" :key="step">
                  {{ step }}
                </li>
              </ol>
            </div>

            <div v-if="canFeedback" class="feedback-actions">
              <div>
                <strong>AI 的建议是否解决了您的问题？</strong>
                <small>选择将影响后续处理方式</small>
              </div>
              <div>
                <el-button
                  :loading="submittingFeedback"
                  :icon="Warning"
                  @click="requestHuman"
                >
                  不满意，转人工
                </el-button>
                <el-button
                  type="primary"
                  :loading="submittingFeedback"
                  :icon="Check"
                  @click="confirmSatisfied"
                >
                  问题已解决
                </el-button>
              </div>
            </div>
          </section>

          <section
            v-if="hasConversation && ['waiting_human', 'human_processing'].includes(ticket.status)"
            class="conversation-callout surface-card"
          >
            <span class="conversation-callout__icon"><el-icon><Headset /></el-icon></span>
            <div>
              <strong>
                {{ ticket.status === 'waiting_human' ? '正在等待平台客服接入' : '平台人工客服处理中' }}
              </strong>
              <p>
                {{ ticket.status === 'waiting_human'
                  ? '客服接入后会与您进行实时沟通，您也可以先留言。'
                  : '人工客服已进入会话，您可以继续补充问题和上传处理信息。' }}
              </p>
            </div>
            <el-button type="primary" :icon="ChatDotRound" @click="enterConversation">
              进入人工会话
            </el-button>
          </section>

          <section class="description-card surface-card">
            <div class="section-heading is-compact">
              <div>
                <span class="section-icon"><el-icon><Box /></el-icon></span>
                <div>
                  <p class="eyebrow">ISSUE</p>
                  <h2>问题信息</h2>
                </div>
              </div>
            </div>
            <dl class="issue-detail">
              <div class="is-full">
                <dt>问题描述</dt>
                <dd>{{ ticket.description }}</dd>
              </div>
              <div v-if="ticket.expected_resolution">
                <dt>期望处理方式</dt>
                <dd>{{ ticket.expected_resolution }}</dd>
              </div>
              <div>
                <dt>AI 分类</dt>
                <dd>{{ ticketCategoryLabel(ticket.category) }}</dd>
              </div>
              <div v-if="ticket.feedback_reason">
                <dt>转人工原因</dt>
                <dd>{{ ticket.feedback_reason }}</dd>
              </div>
              <div v-if="ticket.escalation_reason && ticket.escalation_reason !== ticket.feedback_reason" class="is-full">
                <dt>处理说明</dt>
                <dd>{{ ticket.escalation_reason }}</dd>
              </div>
            </dl>
          </section>

          <section v-if="isClosed" class="closed-card">
            <el-icon><Check /></el-icon>
            <div>
              <strong>本次售后已结束</strong>
              <p>提交于 {{ formatDateTime(ticket.created_at) }} · 最近更新 {{ fromNow(ticket.updated_at) }}</p>
            </div>
          </section>
        </main>

        <aside class="detail-side">
          <section class="side-card order-side-card">
            <div class="side-card__head">
              <h3>关联订单</h3>
              <el-icon><Box /></el-icon>
            </div>
            <p class="order-no">{{ ticket.order?.order_no }}</p>
            <div class="order-product-block">
              <span class="order-product-icon"><el-icon><Box /></el-icon></span>
              <div>
                <strong>{{ ticket.order?.product_name || '订单商品' }}</strong>
                <span>{{ ticket.order?.product_spec || '默认规格' }}</span>
              </div>
            </div>
            <div class="order-side-meta">
              <span>订单状态</span>
              <StatusTag v-if="ticket.order" kind="order" :value="ticket.order.order_status" />
            </div>
            <div class="order-side-meta">
              <span>订单金额</span>
              <strong>{{ formatAmount(ticket.order?.amount || 0) }}</strong>
            </div>
            <div class="side-note">
              <el-icon><Clock /></el-icon>
              <span>提交后由 AI 先处理，遇到无法自动解决的问题再转人工。</span>
            </div>
          </section>

          <section class="side-card timeline-side">
            <h3>处理记录</h3>
            <div class="mini-timeline">
              <div>
                <span class="done" />
                <div>
                  <strong>提交售后申请</strong>
                  <p>{{ formatDateTime(ticket.created_at) }}</p>
                </div>
              </div>
              <div v-if="ticket.ai_reply">
                <span class="done" />
                <div>
                  <strong>AI 生成处理建议</strong>
                  <p>{{ ticketCategoryLabel(ticket.category) }}</p>
                </div>
              </div>
              <div v-if="hasConversation">
                <span :class="{ done: ticket.status !== 'waiting_human' }" />
                <div>
                  <strong>转接人工客服</strong>
                  <p>{{ ticket.status === 'waiting_human' ? '等待接入' : '已接入会话' }}</p>
                </div>
              </div>
              <div v-if="isClosed">
                <span class="done" />
                <div>
                  <strong>售后完成</strong>
                  <p>{{ formatDateTime(ticket.resolved_at || ticket.updated_at) }}</p>
                </div>
              </div>
            </div>
          </section>
        </aside>
      </template>

      <div v-else-if="!loading" class="load-error">
        <p>{{ loadError || '售后单不存在' }}</p>
        <el-button type="primary" @click="router.push('/consumer/after-sales')">
          返回售后服务
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ticket-detail-page {
  max-width: 1180px;
  margin: 0 auto;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 14px;
  padding: 4px 0;
  color: #9999a2;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.back-link:hover {
  color: #ed5a12;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 15px;
  align-items: start;
  min-height: 300px;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.ticket-hero {
  position: relative;
  overflow: hidden;
  padding: 20px 21px 18px;
  border: 1px solid #f0dfd6;
  border-radius: 16px;
  background:
    radial-gradient(circle at 92% 0%, rgba(255, 150, 87, 0.18), transparent 30%),
    linear-gradient(135deg, #fffdfa 0%, #fffaf6 100%);
  box-shadow: 0 10px 28px rgba(50, 33, 24, 0.045);
}

.ticket-hero::after {
  content: '';
  position: absolute;
  right: -70px;
  bottom: -100px;
  width: 230px;
  height: 230px;
  border-radius: 50%;
  background: rgba(255, 144, 75, 0.06);
}

.ticket-hero__top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.ticket-hero__title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 4px;
}

.ticket-hero__title h1 {
  color: #2d2c31;
  font-size: 22px;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.ticket-hero__meta {
  margin-top: 7px;
  color: #a1a1aa;
  font-size: 12px;
}

.ticket-hero__meta span {
  padding: 0 4px;
  color: #d5d5da;
}

.ticket-hero__icon {
  display: grid;
  place-items: center;
  flex: 0 0 46px;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  color: #f06a2e;
  background: #fff0e6;
  font-size: 23px;
}

.status-copy {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid #f7e8df;
}

.status-copy__dot {
  flex: 0 0 6px;
  width: 6px;
  height: 6px;
  margin-top: 6px;
  border-radius: 50%;
  background: #f16d32;
  box-shadow: 0 0 0 3px rgba(241, 109, 50, 0.1);
}

.status-copy strong {
  color: #48444a;
  font-size: 13px;
  font-weight: 650;
}

.status-copy p {
  max-width: 680px;
  margin-top: 4px;
  color: #9d908a;
  font-size: 12px;
  line-height: 1.7;
}

.progress-track {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  margin-top: 20px;
}

.progress-step {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  color: #bbb6b2;
  font-size: 11px;
}

.progress-step__dot {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 19px;
  height: 19px;
  border: 1px solid #e7ddd7;
  border-radius: 50%;
  background: #fffdfb;
  font-size: 11px;
}

.progress-step__line {
  position: absolute;
  top: 9px;
  left: -50%;
  width: 100%;
  height: 1px;
  background: #ede2db;
}

.progress-step.is-done {
  color: #e06329;
}

.progress-step.is-done .progress-step__dot {
  border-color: #ffb38d;
  color: #f0672a;
  background: #fff3eb;
}

.progress-step.is-active {
  color: #df5a1c;
  font-weight: 600;
}

.progress-step.is-active .progress-step__dot {
  border-color: #f1682e;
  color: #fff;
  background: #f1682e;
  box-shadow: 0 0 0 4px rgba(241, 104, 46, 0.1);
}

.face-surface {
  background: #fff;
}

.processing-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 13px;
}

.ai-loader {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  padding: 0 9px;
  border-radius: 10px;
  background: #fff2e8;
}

.ai-loader span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #f06a2e;
  animation: ai-bounce 1.1s infinite ease-in-out;
}

.ai-loader span:nth-child(2) {
  animation-delay: 0.14s;
}

.ai-loader span:nth-child(3) {
  animation-delay: 0.28s;
}

.processing-card strong {
  color: #55555d;
  font-size: 13px;
}

.processing-card p {
  margin-top: 3px;
  color: #a3a3ab;
  font-size: 12px;
}

.ai-result-card,
.description-card {
  padding: 18px;
  border-radius: 14px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.section-heading > div:first-child {
  display: flex;
  align-items: center;
  gap: 9px;
}

.section-heading.is-compact {
  margin-bottom: 14px;
}

.section-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: #eb652c;
  background: #fff2e9;
  font-size: 16px;
}

.section-heading h2 {
  margin-top: 2px;
  color: #3f3f46;
  font-size: 14px;
  font-weight: 650;
}

.category-chip {
  padding: 4px 7px;
  border: 1px solid #ffddc9;
  border-radius: 5px;
  color: #d9622e;
  background: #fff8f3;
  font-size: 12px;
}

.ai-answer {
  margin-top: 14px;
  padding: 12px 13px;
  border-radius: 9px;
  color: #5b5754;
  background: #fbfaf9;
  font-size: 13px;
  line-height: 1.9;
  white-space: pre-wrap;
}

.suggestion-steps {
  margin-top: 12px;
}

.suggestion-steps > span {
  color: #9a9aa2;
  font-size: 12px;
}

.suggestion-steps ol {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 7px;
  padding: 0;
  list-style: none;
}

.suggestion-steps li {
  padding: 4px 8px;
  border-radius: 5px;
  color: #777078;
  background: #f7f5f4;
  font-size: 12px;
}

.feedback-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 17px;
  padding-top: 14px;
  border-top: 1px solid #f2f1f1;
}

.feedback-actions > div:first-child {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.feedback-actions strong {
  color: #5e5d63;
  font-size: 12px;
  font-weight: 600;
}

.feedback-actions small {
  color: #aaaab2;
  font-size: 11px;
}

.feedback-actions > div:last-child {
  display: flex;
  gap: 8px;
}

.feedback-actions :deep(.el-button) {
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  font-size: 13px;
}

.conversation-callout {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 14px 16px;
  border-radius: 13px;
}

.conversation-callout__icon {
  display: grid;
  place-items: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: #19737d;
  background: #eff9f9;
  font-size: 17px;
}

.conversation-callout > div {
  flex: 1;
  min-width: 0;
}

.conversation-callout strong {
  color: #4a5558;
  font-size: 13px;
}

.conversation-callout p {
  margin-top: 3px;
  color: #929b9d;
  font-size: 12px;
}

.conversation-callout :deep(.el-button) {
  flex: 0 0 auto;
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  font-size: 13px;
}

.issue-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 18px;
  margin: 0;
}

.issue-detail div {
  min-width: 0;
}

.issue-detail .is-full {
  grid-column: 1 / -1;
}

.issue-detail dt {
  color: #a4a4ac;
  font-size: 12px;
}

.issue-detail dd {
  margin: 4px 0 0;
  color: #5e5e66;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.closed-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 17px;
  border: 1px solid #e8f5ee;
  border-radius: 13px;
  color: #0f8e63;
  background: #f5fcf8;
}

.closed-card > .el-icon {
  font-size: 18px;
}

.closed-card strong {
  font-size: 13px;
  font-weight: 650;
}

.closed-card p {
  margin-top: 3px;
  color: #83a997;
  font-size: 12px;
}

.detail-side {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.side-card {
  padding: 14px;
  border: 1px solid #ececf1;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 7px 22px rgba(28, 29, 35, 0.03);
}

.side-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.side-card h3 {
  color: #4d4d55;
  font-size: 12px;
  font-weight: 650;
}

.side-card__head :deep(.el-icon) {
  color: #b5b5bd;
  font-size: 14px;
}

.order-no {
  margin-top: 8px;
  color: #aaaab2;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
}

.order-product-block {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 11px;
  padding: 10px;
  border-radius: 9px;
  background: #fafafb;
}

.order-product-icon {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 9px;
  color: #e86a33;
  background: #fff3ea;
  font-size: 17px;
}

.order-product-block > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.order-product-block strong {
  overflow: hidden;
  color: #54545c;
  font-size: 12px;
  font-weight: 550;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-product-block span {
  color: #a4a4ac;
  font-size: 12px;
}

.order-side-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 9px;
  padding-top: 9px;
  border-top: 1px dashed #f1f1f4;
  color: #a1a1a9;
  font-size: 12px;
}

.order-side-meta strong {
  color: #d33f2e;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 14px;
}

.side-note {
  display: flex;
  align-items: flex-start;
  gap: 5px;
  margin-top: 11px;
  padding: 8px;
  border-radius: 7px;
  color: #aaa39c;
  background: #fbf8f5;
  font-size: 11px;
  line-height: 1.6;
}

.timeline-side h3 {
  margin-bottom: 12px;
}

.mini-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.mini-timeline > div {
  position: relative;
  display: flex;
  gap: 9px;
  padding-bottom: 13px;
}

.mini-timeline > div::before {
  content: '';
  position: absolute;
  top: 10px;
  bottom: 0;
  left: 3px;
  width: 1px;
  background: #f0f0f3;
}

.mini-timeline > div:last-child {
  padding-bottom: 0;
}

.mini-timeline > div:last-child::before {
  display: none;
}

.mini-timeline > div > span {
  position: relative;
  z-index: 1;
  flex: 0 0 7px;
  width: 7px;
  height: 7px;
  margin-top: 2px;
  border: 1px solid #dddde3;
  border-radius: 50%;
  background: #fff;
}

.mini-timeline > div > span.done {
  border-color: #f08b5d;
  background: #f08b5d;
}

.mini-timeline > div > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mini-timeline strong {
  color: #75757e;
  font-size: 12px;
  font-weight: 500;
}

.mini-timeline p {
  color: #adadb5;
  font-size: 11px;
}

.load-error {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 20px;
  color: #9b9ba4;
  font-size: 13px;
}

@keyframes ai-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-3px);
    opacity: 1;
  }
}

@media (max-width: 960px) {
  .detail-layout {
    grid-template-columns: minmax(0, 1fr) 270px;
  }
}

@media (max-width: 800px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .detail-side {
    order: -1;
  }

  .ticket-hero__title h1 {
    font-size: 19px;
  }

  .feedback-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .feedback-actions > div:last-child {
    width: 100%;
  }

  .feedback-actions :deep(.el-button) {
    flex: 1;
  }

  .conversation-callout {
    flex-wrap: wrap;
  }

  .issue-detail {
    grid-template-columns: 1fr;
  }

  .progress-step {
    font-size: 11px;
  }
}
</style>
