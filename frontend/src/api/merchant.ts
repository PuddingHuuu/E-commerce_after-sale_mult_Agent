import type {
  ConversationDetail,
  ConversationSummary,
  Message,
  Page,
} from '@/types/api'
import { apiRequest } from './client'

export const merchantApi = {
  getConversations(params: {
    keyword?: string
    page?: number
    page_size?: number
  } = {}): Promise<Page<ConversationSummary>> {
    return apiRequest<Page<ConversationSummary>>('merchant', {
      method: 'GET',
      url: '/merchant/conversations',
      params,
    })
  },

  getConversation(conversationId: number): Promise<ConversationDetail> {
    return apiRequest<ConversationDetail>('merchant', {
      method: 'GET',
      url: `/merchant/conversations/${conversationId}`,
    })
  },

  getMessages(conversationId: number, afterId = 0): Promise<Message[]> {
    return apiRequest<Message[]>('merchant', {
      method: 'GET',
      url: `/merchant/conversations/${conversationId}/messages`,
      params: { after_id: afterId },
    })
  },

  sendMessage(conversationId: number, content: string): Promise<Message> {
    return apiRequest<Message>('merchant', {
      method: 'POST',
      url: `/merchant/conversations/${conversationId}/messages`,
      data: { content },
    })
  },
}
