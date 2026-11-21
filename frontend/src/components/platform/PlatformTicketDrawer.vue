<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowRight,
  Box,
  ChatDotRound,
  Close,
  Cpu,
  Tickets,
} from '@element-plus/icons-vue'
import type { Ticket } from '@/types/api'
import { platformApi } from '@/api/platform'
import { showError } from '@/api/http'
import {
  formatAmount,
  formatDateTime,
  fromNow,
  maskPhone,
} from '@/utils/format'
import {
  agentNameLabels,
  agentStatusLabels,
  ticketCategoryLabel,
} from '@/utils/labels'
import StatusTag from '@/components/common/StatusTag.vue'

const props = defineProps<{
  modelValue: boolean
  ticketId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  updated: []
}>()

const router = useRouter()
const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const ticket = ref<Ticket | null>(null)
const loading = ref(false)
const updating = ref(false)
const expandedRuns = ref<number[]>([])

async function loadTicket(): Promise<void> {
  if (!props.ticketId) return
  loading.value = true
  try {
    ticket.value = await platformApi.getTicket(props.ticketId)
  } catch (error) {
    showError(error)
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.ticketId] as const,
  ([open]) => {
    if (open) void loadTicket()
  },
  { immediate: true },
)

async function updateStatus(status: string): Promise<void> {
  if (!ticket.value || updating.value) return
  updating.value = true
  try {
    ticket.value = await platformApi.updateTicket(ticket.value.id, status)
    ElMessage.success(status === 'resolved' ? '工单已标记为已解决' : '工单已关闭')
    emit('updated')
  } catch (error) {
    showError(error)
  } finally {
    updating.value = false
  }
}

function goConversation(): void {
  if (!ticket.value?.conversation_id) return
  visible.value = false
  router.push({
    path: '/platform/conversations',
    query: { conversation: String(ticket.value.conversation_id) },
  })
}

function toggleRun(runId: number): void {
  if (expandedRuns.value.includes(runId)) {
    expandedRuns.value = expandedRuns.value.filter((id) => id !== runId)
  } else {
    expandedRuns.value = [...expandedRuns.value, runId]
  }
}

function runSummary(runId: number): string {
  const run = ticket.value?.agent_runs.find((item) => item.id === runId)
  if (!run?.output_json) return '暂无结构化输出'
  return JSON.stringify(run.output_json, null, 2)
}
</script>

<template>
  <el-drawer
    v-model="visible"
    class="as-drawer"
    size="660px"
    :with-header="false"
    append-to-body
  >
    <div v-if="ticket" v-loading="loading" class="ticket-drawer">
      <header class="drawer-head">
        <div class="drawer-head__left">
          <span class="drawer-head__icon"><el-icon><Tickets /></el-icon></span>
          <div>
            <p class="eyebrow">TICKET DETAIL</p>
            <div class="drawer-title-row">
              <h2>{{ ticketCategoryLabel(ticket.category) }}工单</h2>
              <StatusTag kind="ticket" :value="ticket.status" dot />
            </div>
            <p class="ticket-no">{{ ticket.ticket_no }}</p>
          </div>
        </div>
        <button type="button" class="drawer-close" @click="visible = false">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <div class="drawer-scroll">
        <section class="summary-strip">
          <div>
            <span>消费者</span>
            <strong>{{ ticket.customer_name }}</strong>
          </div>
          <div>
            <span>联系电话</span>
            <strong>{{ maskPhone(ticket.customer_phone || '') || '—' }}</strong>
          </div>
          <div>
            <span>优先级</span>
            <StatusTag kind="priority" :value="ticket.priority" />
          </div>
          <div>
            <span>处理人</span>
            <strong>{{ ticket.assignee_name || '未接入' }}</strong>
          </div>
        </section>

        <section class="detail-card">
          <div class="card-title">
            <h3>问题信息</h3>
            <span>{{ formatDateTime(ticket.created_at) }}</span>
          </div>
          <h4>{{ ticket.subject }}</h4>
          <p class="description">{{ ticket.description }}</p>
          <div v-if="ticket.expected_resolution" class="expected">
            期望处理方式：{{ ticket.expected_resolution }}
          </div>
          <div class="meta-grid">
            <div>
              <span>AI 分类置信度</span>
              <strong>{{ ticket.confidence ? `${Math.round(ticket.confidence * 100)}%` : '—' }}</strong>
            </div>
            <div>
              <span>转人工原因</span>
              <strong>{{ ticket.escalation_reason || '—' }}</strong>
            </div>
            <div>
              <span>用户反馈</span>
              <strong>{{ ticket.feedback_result === 'satisfied' ? '已解决' : ticket.feedback_result === 'dissatisfied' ? '不满意' : '—' }}</strong>
            </div>
            <div>
              <span>最后更新</span>
              <strong>{{ fromNow(ticket.updated_at) }}</strong>
            </div>
          </div>
        </section>

        <section class="detail-card">
          <div class="card-title">
            <h3>关联订单</h3>
            <span v-if="ticket.order">{{ ticket.order.order_no }}</span>
          </div>
          <div v-if="ticket.order" class="linked-order">
            <span class="linked-order__thumb"><el-icon><Box /></el-icon></span>
            <div class="linked-order__copy">
              <strong>{{ ticket.order.product_name }}</strong>
              <span>{{ ticket.order.product_spec || '默认规格' }}</span>
            </div>
            <div class="linked-order__end">
              <strong>{{ formatAmount(ticket.order.amount || 0) }}</strong>
              <StatusTag kind="order" :value="ticket.order.order_status" />
            </div>
          </div>
        </section>

        <section v-if="ticket.ai_reply" class="detail-card ai-card">
          <div class="card-title">
            <h3>AI 处理结果</h3>
            <span>{{ ticket.ai_result_json?.model || 'AI' }}</span>
          </div>
          <div class="ai-reply">{{ ticket.ai_reply }}</div>
          <div v-if="ticket.ai_result_json?.steps?.length" class="ai-steps">
            <span v-for="(step, index) in ticket.ai_result_json.steps" :key="step">
              {{ index + 1 }} · {{ step }}
            </span>
          </div>
        </section>

        <section class="detail-card">
          <div class="card-title">
            <h3>Agent 处理链路</h3>
            <span>{{ ticket.agent_runs.length }} 个步骤</span>
          </div>

          <div v-if="ticket.agent_runs.length" class="agent-trace">
            <div
              v-for="run in ticket.agent_runs"
              :key="run.id"
              class="agent-run"
              :class="{ 'is-open': expandedRuns.includes(run.id) }"
            >
              <button type="button" class="agent-run__head" @click="toggleRun(run.id)">
                <span class="agent-run__dot" :class="`is-${run.status}`" />
                <span class="agent-run__name">
                  <el-icon><Cpu /></el-icon>
                  {{ agentNameLabels[run.agent_name] || run.agent_name }}
                </span>
                <span class="agent-run__status">
                  {{ agentStatusLabels[run.status] || run.status }}
                </span>
                <span class="agent-run__model">{{ run.model_name || '规则' }}</span>
                <span v-if="run.duration_ms !== null" class="agent-run__duration">{{ run.duration_ms }}ms</span>
                <el-icon class="agent-run__arrow"><ArrowRight /></el-icon>
              </button>
              <div v-if="expandedRuns.includes(run.id)" class="agent-run__body">
                <p v-if="run.error_message" class="run-error">{{ run.error_message }}</p>
                <pre>{{ runSummary(run.id) }}</pre>
              </div>
            </div>
          </div>
          <p v-else class="empty-text">暂无 Agent 日志</p>
        </section>

        <section v-if="ticket.conversation_id" class="detail-card conversation-link">
          <span class="conversation-link__icon"><el-icon><ChatDotRound /></el-icon></span>
          <div>
            <h3>关联人工会话</h3>
            <p>当前工单已关联人工客服会话，可进入查看聊天记录。</p>
          </div>
          <el-button size="small" type="primary" @click="goConversation">进入会话</el-button>
        </section>
      </div>

      <footer class="drawer-foot">
        <span class="foot-note">工单内容仅平台客服可见</span>
        <div>
          <el-button
            v-if="!['resolved', 'closed'].includes(ticket.status)"
            :loading="updating"
            @click="updateStatus('closed')"
          >
            关闭工单
          </el-button>
          <el-button
            v-if="!['resolved', 'closed'].includes(ticket.status)"
            type="primary"
            :loading="updating"
            @click="updateStatus('resolved')"
          >
            标记已解决
          </el-button>
        </div>
      </footer>
    </div>

    <div v-else v-loading="loading" class="drawer-loading" />
  </el-drawer>
</template>

<style scoped>
.ticket-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f2f6fc;
}

.drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex: 0 0 auto;
  padding: 21px 23px 17px;
  border-bottom: 1px solid #ececf1;
  background: #fff;
}

.drawer-head__left {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.drawer-head__icon {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  color: #2f6fe4;
  background: #eef4ff;
  font-size: 20px;
}

.drawer-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
}

.drawer-title-row h2 {
  color: #2e2e34;
  font-size: 19px;
  font-weight: 700;
}

.ticket-no {
  margin-top: 4px;
  color: #a6a6ae;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
  letter-spacing: 0.03em;
}

.drawer-close {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  color: #96969f;
  background: #f6f6f8;
  font-size: 15px;
  cursor: pointer;
}

.drawer-scroll {
  flex: 1;
  min-height: 0;
  padding: 16px 19px 24px;
  overflow-y: auto;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 14px;
  border: 1px solid #ececf1;
  border-radius: 12px;
  background: #fff;
}

.summary-strip div {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.summary-strip span {
  color: #a4a4ac;
  font-size: 12px;
}

.summary-strip strong {
  overflow: hidden;
  color: #66666f;
  font-size: 13px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-card {
  margin-top: 12px;
  padding: 15px;
  border: 1px solid #ececf1;
  border-radius: 12px;
  background: #fff;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 11px;
}

.card-title h3 {
  color: #45454d;
  font-size: 13px;
  font-weight: 650;
}

.card-title > span {
  color: #aaaab2;
  font-size: 12px;
}

.detail-card h4 {
  color: #3f3f46;
  font-size: 14px;
  font-weight: 600;
}

.description {
  margin-top: 7px;
  color: #696972;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.expected {
  margin-top: 9px;
  padding: 8px 10px;
  border-radius: 7px;
  color: #5f6f8f;
  background: #f5f8ff;
  font-size: 12px;
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 15px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed #f0f0f4;
}

.meta-grid div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-grid span {
  color: #aaaab2;
  font-size: 11px;
}

.meta-grid strong {
  color: #6a6a73;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.55;
}

.linked-order {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px;
  border-radius: 8px;
  background: #fafafb;
}

.linked-order__thumb {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 8px;
  color: #2f6fe4;
  background: #eef4ff;
  font-size: 16px;
}

.linked-order__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.linked-order__copy strong {
  overflow: hidden;
  color: #57575f;
  font-size: 12px;
  font-weight: 550;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.linked-order__copy span {
  color: #a4a4ac;
  font-size: 12px;
}

.linked-order__end {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.linked-order__end > strong {
  color: #d33e2e;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 13px;
}

.ai-card {
  background: linear-gradient(180deg, #fff, #f5f9ff);
}

.ai-reply {
  padding: 11px 12px;
  border-left: 3px solid #9fc0f4;
  border-radius: 0 8px 8px 0;
  color: #44506b;
  background: #eef4ff;
  font-size: 12px;
  line-height: 1.85;
  white-space: pre-wrap;
}

.ai-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 9px;
}

.ai-steps span {
  padding: 3px 7px;
  border-radius: 4px;
  color: #6b7a99;
  background: #f3f7ff;
  font-size: 11px;
}

.agent-trace {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.agent-run {
  overflow: hidden;
  border: 1px solid #f0f0f4;
  border-radius: 8px;
}

.agent-run.is-open {
  border-color: #dbe6f5;
}

.agent-run__head {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 100%;
  padding: 10px 11px;
  text-align: left;
  background: #fff;
  cursor: pointer;
}

.agent-run__dot {
  flex: 0 0 6px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #12a977;
}

.agent-run__dot.is-failed {
  background: #d63428;
}

.agent-run__dot.is-fallback {
  background: #e4941e;
}

.agent-run__name {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #5c5c65;
  font-size: 12px;
  font-weight: 550;
}

.agent-run__status {
  padding: 2px 5px;
  border-radius: 3px;
  color: #0e8f65;
  background: #edf9f4;
  font-size: 11px;
}

.agent-run__model {
  margin-left: auto;
  color: #b1b1b9;
  font-size: 11px;
}

.agent-run__duration {
  color: #b1b1b9;
  font-size: 11px;
}

.agent-run__arrow {
  color: #c2c2ca;
  font-size: 12px;
  transition: transform 0.2s ease;
}

.agent-run.is-open .agent-run__arrow {
  transform: rotate(90deg);
}

.agent-run__body {
  padding: 8px 10px 10px;
  border-top: 1px solid #f5f5f7;
  background: #fbfbfc;
}

.agent-run__body pre {
  max-height: 180px;
  margin: 0;
  padding: 8px;
  overflow: auto;
  border-radius: 5px;
  color: #67676f;
  background: #f3f3f6;
  font-family: 'Cascadia Code', 'SFMono-Regular', Consolas, monospace;
  font-size: 11px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.run-error {
  margin-bottom: 7px;
  color: #c44532;
  font-size: 12px;
}

.empty-text {
  color: #aaaab2;
  font-size: 12px;
}

.conversation-link {
  display: flex;
  align-items: center;
  gap: 10px;
}

.conversation-link__icon {
  display: grid;
  place-items: center;
  width: 37px;
  height: 37px;
  border-radius: 9px;
  color: #238181;
  background: #edf8f8;
  font-size: 16px;
}

.conversation-link > div {
  flex: 1;
  min-width: 0;
}

.conversation-link h3 {
  color: #4a4a52;
  font-size: 12px;
  font-weight: 600;
}

.conversation-link p {
  margin-top: 3px;
  color: #a0a0a8;
  font-size: 12px;
}

.drawer-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex: 0 0 auto;
  padding: 12px 19px;
  border-top: 1px solid #ececf1;
  background: #fff;
}

.foot-note {
  color: #aaaab2;
  font-size: 11px;
}

.drawer-foot > div {
  display: flex;
  gap: 8px;
}

.drawer-foot :deep(.el-button) {
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  font-size: 13px;
}

.drawer-loading {
  height: 100%;
}

@media (max-width: 660px) {
  .summary-strip {
    grid-template-columns: 1fr 1fr;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .drawer-foot {
    align-items: flex-end;
  }

  .foot-note {
    display: none;
  }
}
</style>
