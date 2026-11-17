import type {
  ConversationStatus,
  OrderStatus,
  TicketPriority,
  TicketStatus,
  TicketType,
} from '@/types'

export type Tone = 'blue' | 'amber' | 'green' | 'gray' | 'red' | 'orange' | 'violet'

export interface Meta {
  label: string
  tone: Tone
}

export const conversationStatusMeta: Record<ConversationStatus, Meta> = {
  ai: { label: 'AI 接待中', tone: 'blue' },
  waiting: { label: '等待人工', tone: 'amber' },
  human: { label: '人工服务中', tone: 'green' },
  closed: { label: '已结束', tone: 'gray' },
}

export const orderStatusMeta: Record<OrderStatus, Meta> = {
  pending_payment: { label: '待付款', tone: 'amber' },
  pending_shipment: { label: '待发货', tone: 'orange' },
  shipped: { label: '运输中', tone: 'blue' },
  received: { label: '已签收', tone: 'green' },
  completed: { label: '已完成', tone: 'gray' },
  cancelled: { label: '已取消', tone: 'gray' },
  refunding: { label: '退款中', tone: 'red' },
}

export const ticketStatusMeta: Record<TicketStatus, Meta> = {
  pending: { label: '待处理', tone: 'amber' },
  processing: { label: '处理中', tone: 'blue' },
  resolved: { label: '已解决', tone: 'green' },
  closed: { label: '已关闭', tone: 'gray' },
}

export const priorityMeta: Record<TicketPriority, Meta> = {
  low: { label: '低', tone: 'gray' },
  normal: { label: '中', tone: 'blue' },
  high: { label: '高', tone: 'orange' },
  urgent: { label: '紧急', tone: 'red' },
}

export const ticketTypeLabels: Record<TicketType, string> = {
  refund_only: '仅退款',
  return_refund: '退货退款',
  exchange: '换货',
  repair: '维修',
  logistics: '物流异常',
  other: '其他问题',
}

export const orderStatusOptions = (
  Object.entries(orderStatusMeta) as [OrderStatus, Meta][]
).map(([value, meta]) => ({ value, label: meta.label }))

export const ticketStatusOptions = (
  Object.entries(ticketStatusMeta) as [TicketStatus, Meta][]
).map(([value, meta]) => ({ value, label: meta.label }))

export const priorityOptions = (
  Object.entries(priorityMeta) as [TicketPriority, Meta][]
).map(([value, meta]) => ({ value, label: meta.label }))

export const ticketTypeOptions = (
  Object.entries(ticketTypeLabels) as [TicketType, string][]
).map(([value, label]) => ({ value, label }))

export function ticketTypeLabel(type: TicketType): string {
  return ticketTypeLabels[type] ?? type
}
