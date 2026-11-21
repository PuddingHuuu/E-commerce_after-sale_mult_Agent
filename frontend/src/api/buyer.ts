import type {
  ConversationDetail,
  ConversationSummary,
  FeedbackResponse,
  Message,
  Order,
  Page,
  Ticket,
} from '@/types/api'
import { apiRequest } from './client'

export interface BuyerOrderQuery {
  tab?: string
  keyword?: string
  page?: number
  page_size?: number
}

export interface CreateTicketPayload {
  order_id: number
  description: string
  expected_resolution?: string | null
}

export const buyerApi = {
  getOrders(params: BuyerOrderQuery = {}): Promise<Page<Order>> {
    return apiRequest<Page<Order>>('consumer', {
      method: 'GET',
      url: '/buyer/orders',
      params,
    })
  },

  getOrder(orderId: number): Promise<Order> {
    return apiRequest<Order>('consumer', {
      method: 'GET',
      url: `/buyer/orders/${orderId}`,
    })
  },

  createTicket(payload: CreateTicketPayload): Promise<Ticket> {
    return apiRequest<Ticket>('consumer', {
      method: 'POST',
      url: '/buyer/tickets',
      data: payload,
    })
  },

  listTickets(params: { page?: number; page_size?: number } = {}): Promise<Page<Ticket>> {
    return apiRequest<Page<Ticket>>('consumer', {
      method: 'GET',
      url: '/buyer/tickets',
      params,
    })
  },

  getTicket(ticketId: number): Promise<Ticket> {
    return apiRequest<Ticket>('consumer', {
      method: 'GET',
      url: `/buyer/tickets/${ticketId}`,
    })
  },

  feedback(
    ticketId: number,
    payload: { satisfied: boolean; reason?: string | null },
  ): Promise<FeedbackResponse> {
    return apiRequest<FeedbackResponse>('consumer', {
      method: 'POST',
      url: `/buyer/tickets/${ticketId}/feedback`,
      data: payload,
    })
  },

  getConversations(params: { keyword?: string; page?: number; page_size?: number } = {}): Promise<Page<ConversationSummary>> {
    return apiRequest<Page<ConversationSummary>>('consumer', {
      method: 'GET',
      url: '/buyer/conversations',
      params,
    })
  },

  getConversation(conversationId: number): Promise<ConversationDetail> {
    return apiRequest<ConversationDetail>('consumer', {
      method: 'GET',
      url: `/buyer/conversations/${conversationId}`,
    })
  },

  getMessages(conversationId: number, afterId = 0): Promise<Message[]> {
    return apiRequest<Message[]>('consumer', {
      method: 'GET',
      url: `/buyer/conversations/${conversationId}/messages`,
      params: { after_id: afterId },
    })
  },

  sendMessage(conversationId: number, content: string): Promise<Message> {
    return apiRequest<Message>('consumer', {
      method: 'POST',
      url: `/buyer/conversations/${conversationId}/messages`,
      data: { content },
    })
  },
}
