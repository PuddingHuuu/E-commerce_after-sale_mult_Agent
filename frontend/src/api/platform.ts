import type {
  ConversationDetail,
  ConversationSummary,
  MerchantOption,
  Message,
  Order,
  Page,
  Ticket,
} from '@/types/api'
import { apiRequest } from './client'

export interface PlatformTicketQuery {
  group?: string
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}

export interface PlatformOrderQuery {
  keyword?: string
  status?: string
  page?: number
  page_size?: number
}

export interface PlatformConversationQuery {
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}

export const platformApi = {
  getTickets(params: PlatformTicketQuery = {}): Promise<Page<Ticket>> {
    return apiRequest<Page<Ticket>>('platform', {
      method: 'GET',
      url: '/platform/tickets',
      params,
    })
  },

  getTicket(ticketId: number): Promise<Ticket> {
    return apiRequest<Ticket>('platform', {
      method: 'GET',
      url: `/platform/tickets/${ticketId}`,
    })
  },

  updateTicket(ticketId: number, status: string): Promise<Ticket> {
    return apiRequest<Ticket>('platform', {
      method: 'PATCH',
      url: `/platform/tickets/${ticketId}`,
      data: { status },
    })
  },

  getOrders(params: PlatformOrderQuery = {}): Promise<Page<Order>> {
    return apiRequest<Page<Order>>('platform', {
      method: 'GET',
      url: '/platform/orders',
      params,
    })
  },

  getOrder(orderId: number): Promise<Order> {
    return apiRequest<Order>('platform', {
      method: 'GET',
      url: `/platform/orders/${orderId}`,
    })
  },

  getConversations(params: PlatformConversationQuery = {}): Promise<Page<ConversationSummary>> {
    return apiRequest<Page<ConversationSummary>>('platform', {
      method: 'GET',
      url: '/platform/conversations',
      params,
    })
  },

  getConversation(conversationId: number): Promise<ConversationDetail> {
    return apiRequest<ConversationDetail>('platform', {
      method: 'GET',
      url: `/platform/conversations/${conversationId}`,
    })
  },

  getMessages(conversationId: number, afterId = 0): Promise<Message[]> {
    return apiRequest<Message[]>('platform', {
      method: 'GET',
      url: `/platform/conversations/${conversationId}/messages`,
      params: { after_id: afterId },
    })
  },

  acceptConversation(conversationId: number): Promise<ConversationSummary> {
    return apiRequest<ConversationSummary>('platform', {
      method: 'POST',
      url: `/platform/conversations/${conversationId}/accept`,
    })
  },

  sendMessage(conversationId: number, content: string): Promise<Message> {
    return apiRequest<Message>('platform', {
      method: 'POST',
      url: `/platform/conversations/${conversationId}/messages`,
      data: { content },
    })
  },

  searchMerchants(keyword = ''): Promise<MerchantOption[]> {
    return apiRequest<MerchantOption[]>('platform', {
      method: 'GET',
      url: '/platform/merchants',
      params: { keyword },
    })
  },

  inviteMerchant(conversationId: number, merchantId: number): Promise<{
    conversation: ConversationSummary
    merchant: MerchantOption
  }> {
    return apiRequest('platform', {
      method: 'POST',
      url: `/platform/conversations/${conversationId}/invite-merchant`,
      data: { merchant_id: merchantId },
    })
  },

  closeConversation(conversationId: number): Promise<ConversationSummary> {
    return apiRequest<ConversationSummary>('platform', {
      method: 'POST',
      url: `/platform/conversations/${conversationId}/close`,
    })
  },
}
