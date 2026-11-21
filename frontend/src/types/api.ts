export type Role = 'consumer' | 'platform' | 'merchant'

export interface AuthUser {
  id: number
  role: Role
  login_name: string
  display_name: string
  phone: string | null
  merchant_id?: number | null
  store_name?: string | null
}

export interface AuthResponse {
  token: string
  expires_at: string
  user: AuthUser
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  counts?: Record<string, number> | null
}

export interface OrderItem {
  id: number
  product_id: number | null
  sku_id: string | null
  product_name: string
  sku_spec: string | null
  unit_price: string
  quantity: number
  item_amount: string
  discount_amount: string
  pay_amount: string
  refund_quantity: number
  refund_amount: string
}

export interface Order {
  id: number
  order_no: string
  user_id: number
  shop_id: number
  order_status: string
  payment_status: string
  shipping_status: string
  after_sale_status: string
  currency: string
  goods_amount: string
  discount_amount: string
  freight_amount: string
  payable_amount: string
  paid_amount: string
  refund_amount: string
  payment_method: string | null
  order_source: string
  buyer_note: string | null
  cancel_reason: string | null
  receiver_name: string
  receiver_phone: string
  receiver_city: string | null
  receiver_address: string | null
  logistics_company: string | null
  tracking_no: string | null
  item_count: number
  paid_at: string | null
  shipped_at: string | null
  received_at: string | null
  completed_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
  items: OrderItem[]
  customer_name?: string | null
  customer_phone?: string | null
  ticket_count?: number
  latest_ticket_no?: string | null
  latest_ticket_status?: string | null
}

export interface AgentRun {
  id: number
  agent_name: string
  sequence: number
  status: string
  model_name: string | null
  prompt_version: string | null
  input_json: Record<string, unknown> | null
  output_json: Record<string, unknown> | null
  error_message: string | null
  prompt_tokens: number | null
  completion_tokens: number | null
  duration_ms: number | null
  created_at: string
}

export interface TicketOrder {
  id: number
  order_no: string
  order_status: string
  product_name: string
  product_spec: string | null
  amount: string | null
}

export interface Ticket {
  id: number
  ticket_no: string
  subject: string
  description: string
  expected_resolution: string | null
  category: string | null
  confidence: number | null
  status: string
  priority: string
  ai_reply: string | null
  ai_result_json: {
    category?: string
    confidence?: number
    steps?: string[]
    facts?: Record<string, unknown>
    reply?: string
    model?: string
  } | null
  escalation_reason: string | null
  feedback_result: string | null
  feedback_reason: string | null
  conversation_id: number | null
  created_at: string
  updated_at: string
  resolved_at: string | null
  order: TicketOrder | null
  agent_runs: AgentRun[]
  customer_id?: number
  customer_name?: string
  customer_phone?: string | null
  assignee_id?: number | null
  assignee_name?: string | null
  linked_conversation_status?: string | null
}

export interface FeedbackResponse {
  ticket: Ticket
  conversation_id: number | null
}

export interface ConversationSummary {
  id: number
  status: string
  customer_id: number
  customer_name: string
  order_id: number | null
  order_no: string | null
  order_product: string | null
  assigned_agent_name: string | null
  merchant_id: number | null
  merchant_name: string | null
  last_message: string | null
  ticket_numbers: string[]
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  conversation_id: number
  sender_type: 'customer' | 'platform' | 'merchant' | 'system'
  sender_id: number | null
  sender_name: string | null
  content: string
  created_at: string
}

export interface LinkedTicket {
  id: number
  ticket_no: string
  subject: string
  status: string
  category: string | null
  updated_at: string
}

export interface ConversationDetail {
  conversation: ConversationSummary
  messages: Message[]
  linked_tickets: LinkedTicket[]
}

export interface MerchantOption {
  id: number
  store_name: string
  contact_name: string | null
  phone: string | null
}
