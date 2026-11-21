import type { Role } from '@/types/api'

export type Tone = 'blue' | 'amber' | 'green' | 'gray' | 'red' | 'orange' | 'violet'

export interface Meta {
  label: string
  tone: Tone
}

export const roleMeta: Record<Role, { label: string; subtitle: string; home: string; accent: string }> = {
  consumer: {
    label: '消费者',
    subtitle: '我的订单与售后',
    home: '/consumer/orders',
    accent: '#ff5000',
  },
  platform: {
    label: '平台客服',
    subtitle: '工单与会话工作台',
    home: '/platform/tickets',
    accent: '#e1251b',
  },
  merchant: {
    label: '商家',
    subtitle: '协同会话',
    home: '/merchant/conversations',
    accent: '#138a8a',
  },
}

export const orderStatusMeta: Record<string, Meta> = {
  pending_payment: { label: '待付款', tone: 'amber' },
  pending_shipment: { label: '待发货', tone: 'orange' },
  shipped: { label: '待收货', tone: 'blue' },
  received: { label: '待评价', tone: 'violet' },
  completed: { label: '已完成', tone: 'gray' },
  refunding: { label: '退款中', tone: 'red' },
  cancelled: { label: '已取消', tone: 'gray' },
}

export const ticketStatusMeta: Record<string, Meta> = {
  ai_processing: { label: 'AI 处理中', tone: 'blue' },
  awaiting_feedback: { label: '待用户反馈', tone: 'violet' },
  waiting_human: { label: '等待人工接入', tone: 'amber' },
  human_processing: { label: '人工处理中', tone: 'green' },
  resolved: { label: '已解决', tone: 'green' },
  closed: { label: '已关闭', tone: 'gray' },
}

export const conversationStatusMeta: Record<string, Meta> = {
  waiting: { label: '等待接入', tone: 'amber' },
  human: { label: '人工处理中', tone: 'green' },
  closed: { label: '已结束', tone: 'gray' },
}

export const priorityMeta: Record<string, Meta> = {
  low: { label: '低', tone: 'gray' },
  normal: { label: '中', tone: 'blue' },
  high: { label: '高', tone: 'orange' },
  urgent: { label: '紧急', tone: 'red' },
}

export const ticketCategoryLabels: Record<string, string> = {
  refund_only: '仅退款',
  return_refund: '退货退款',
  exchange: '换货',
  repair: '维修 / 质量问题',
  logistics: '物流异常',
  other: '其他问题',
}

export const orderSourceLabels: Record<string, string> = {
  app: 'APP',
  web: '网页',
  h5: 'H5',
  mini_program: '小程序',
  customer_service: '客服代下单',
}

export const paymentMethodLabels: Record<string, string> = {
  wechat: '微信支付',
  alipay: '支付宝',
  bank_card: '银行卡',
}

export const senderLabels: Record<string, string> = {
  customer: '消费者',
  platform: '平台客服',
  merchant: '商家客服',
  system: '系统',
}

export const buyerOrderTabs = [
  { key: 'all', label: '全部' },
  { key: 'pending_payment', label: '待付款' },
  { key: 'pending_shipment', label: '待发货' },
  { key: 'shipped', label: '待收货' },
  { key: 'received', label: '待评价' },
  { key: 'completed', label: '已完成' },
  { key: 'after_sale', label: '退款/售后' },
  { key: 'cancelled', label: '已取消' },
]

export const platformTicketGroups = [
  { key: 'ai', label: 'AI 处理中' },
  { key: 'human', label: '转人工' },
  { key: 'ended', label: '已结束' },
]

export const platformConversationFilters = [
  { key: '', label: '全部' },
  { key: 'waiting', label: '等待接入' },
  { key: 'human', label: '人工处理中' },
  { key: 'closed', label: '已结束' },
]

export const agentNameLabels: Record<string, string> = {
  classification: '分类 Agent',
  retrieval: '数据检索 Agent',
  reply: '回复 Agent',
  handoff: '转人工',
}

export const agentStatusLabels: Record<string, string> = {
  success: '成功',
  failed: '失败',
  fallback: '规则降级',
}

export const afterSaleEligibleStatuses = new Set([
  'pending_shipment',
  'shipped',
  'received',
  'completed',
  'refunding',
])

export function getOrderStatus(status: string): Meta {
  return orderStatusMeta[status] ?? { label: status, tone: 'gray' }
}

export function getTicketStatus(status: string): Meta {
  return ticketStatusMeta[status] ?? { label: status, tone: 'gray' }
}

export function getConversationStatus(status: string): Meta {
  return conversationStatusMeta[status] ?? { label: status, tone: 'gray' }
}

export function getPriority(status: string): Meta {
  return priorityMeta[status] ?? { label: status, tone: 'gray' }
}

export function ticketCategoryLabel(category: string | null | undefined): string {
  if (!category) return '待分类'
  return ticketCategoryLabels[category] ?? category
}
