export type ConversationStatus = 'ai' | 'waiting' | 'human' | 'closed'

export type SenderType = 'customer' | 'ai' | 'agent' | 'system'

export type OrderStatus =
  | 'pending_payment'
  | 'pending_shipment'
  | 'shipped'
  | 'received'
  | 'completed'
  | 'cancelled'
  | 'refunding'

export type TicketType =
  | 'refund_only'
  | 'return_refund'
  | 'exchange'
  | 'repair'
  | 'logistics'
  | 'other'

export type TicketPriority = 'low' | 'normal' | 'high' | 'urgent'

export type TicketStatus = 'pending' | 'processing' | 'resolved' | 'closed'

export interface Customer {
  id: number
  name: string
  phone: string
  joinedAt: string
}

export interface Conversation {
  id: number
  customerId: number
  title: string
  status: ConversationStatus
  agentName: string | null
  lastMessage: string
  createdAt: string
  updatedAt: string
  waitingSince: string | null
  closedAt: string | null
}

export interface ChatMessage {
  id: number
  conversationId: number
  senderType: SenderType
  content: string
  createdAt: string
}

export interface Order {
  id: number
  orderNo: string
  customerId: number
  productName: string
  productSpec: string
  quantity: number
  amount: number
  orderStatus: OrderStatus
  logisticsCompany: string
  trackingNo: string
  createdAt: string
  updatedAt: string
}

export interface Ticket {
  id: number
  ticketNo: string
  orderId: number
  customerId: number
  conversationId: number | null
  type: TicketType
  description: string
  priority: TicketPriority
  status: TicketStatus
  assignee: string
  createdAt: string
  updatedAt: string
  resolvedAt: string | null
}

export interface DemoDatabase {
  version: number
  customers: Customer[]
  conversations: Conversation[]
  messages: ChatMessage[]
  orders: Order[]
  tickets: Ticket[]
}

export interface CreateTicketInput {
  orderId: number
  conversationId?: number | null
  type: TicketType
  description: string
  priority: TicketPriority
}
