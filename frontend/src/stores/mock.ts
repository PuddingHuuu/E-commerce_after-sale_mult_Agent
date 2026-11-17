import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import dayjs from 'dayjs'
import type {
  ChatMessage,
  Conversation,
  CreateTicketInput,
  Customer,
  DemoDatabase,
  Order,
  SenderType,
  Ticket,
} from '@/types'
import {
  DB_CHANNEL_NAME,
  DB_STORAGE_KEY,
  DEMO_AGENT_NAME,
  DEMO_CUSTOMER_ID,
} from '@/config'
import { createInitialDatabase, DB_VERSION } from '@/mock/seed'
import { buildMockAiReply, buildWelcomeMessage, simulateNetworkDelay } from '@/mock/ai'
import { truncate } from '@/utils/format'

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function isDatabase(value: unknown): value is DemoDatabase {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<DemoDatabase>
  return (
    candidate.version === DB_VERSION &&
    Array.isArray(candidate.customers) &&
    Array.isArray(candidate.conversations) &&
    Array.isArray(candidate.messages) &&
    Array.isArray(candidate.orders) &&
    Array.isArray(candidate.tickets)
  )
}

function writeDatabase(value: DemoDatabase): void {
  localStorage.setItem(DB_STORAGE_KEY, JSON.stringify(value))
}

function readDatabase(): DemoDatabase {
  try {
    const raw = localStorage.getItem(DB_STORAGE_KEY)
    if (raw) {
      const parsed: unknown = JSON.parse(raw)
      if (isDatabase(parsed)) return parsed
    }
  } catch {
    // Corrupted demo data is replaced with a clean seed below.
  }

  const seeded = createInitialDatabase()
  writeDatabase(seeded)
  return seeded
}

function nextId(items: { id: number }[]): number {
  return Math.max(0, ...items.map((item) => item.id)) + 1
}

export const useMockStore = defineStore('mock', () => {
  const db = ref<DemoDatabase>(readDatabase())
  const typingConversationId = ref<number | null>(null)

  let channel: BroadcastChannel | null = null

  if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
    channel = new BroadcastChannel(DB_CHANNEL_NAME)
    channel.onmessage = () => {
      db.value = readDatabase()
    }
    window.addEventListener('storage', (event) => {
      if (event.key === DB_STORAGE_KEY) {
        db.value = readDatabase()
      }
    })
  }

  function commit<T>(mutator: (draft: DemoDatabase) => T): T {
    const latest = readDatabase()
    const result = mutator(latest)
    writeDatabase(latest)
    db.value = latest
    channel?.postMessage({ type: 'sync' })
    return result
  }

  function notifyOtherTabs(): void {
    channel?.postMessage({ type: 'sync' })
  }

  const currentCustomer = computed<Customer>(() => {
    return (
      db.value.customers.find((customer) => customer.id === DEMO_CUSTOMER_ID) ??
      db.value.customers[0]
    )
  })

  function customerById(id: number): Customer | undefined {
    return db.value.customers.find((customer) => customer.id === id)
  }

  function conversationById(id: number): Conversation | undefined {
    return db.value.conversations.find((conversation) => conversation.id === id)
  }

  function messagesFor(conversationId: number): ChatMessage[] {
    return db.value.messages
      .filter((message) => message.conversationId === conversationId)
      .sort((a, b) => a.id - b.id)
  }

  function customerConversations(customerId = DEMO_CUSTOMER_ID): Conversation[] {
    return db.value.conversations
      .filter((conversation) => conversation.customerId === customerId)
      .sort((a, b) => dayjs(b.updatedAt).valueOf() - dayjs(a.updatedAt).valueOf())
  }

  function orderById(id: number): Order | undefined {
    return db.value.orders.find((order) => order.id === id)
  }

  function ordersForCustomer(customerId: number): Order[] {
    return db.value.orders
      .filter((order) => order.customerId === customerId)
      .sort((a, b) => dayjs(b.createdAt).valueOf() - dayjs(a.createdAt).valueOf())
  }

  function ticketById(id: number): Ticket | undefined {
    return db.value.tickets.find((ticket) => ticket.id === id)
  }

  function ticketsForOrder(orderId: number): Ticket[] {
    return db.value.tickets
      .filter((ticket) => ticket.orderId === orderId)
      .sort((a, b) => dayjs(b.createdAt).valueOf() - dayjs(a.createdAt).valueOf())
  }

  function ticketsForCustomer(customerId: number): Ticket[] {
    return db.value.tickets
      .filter((ticket) => ticket.customerId === customerId)
      .sort((a, b) => dayjs(b.updatedAt).valueOf() - dayjs(a.updatedAt).valueOf())
  }

  function ticketsForConversation(conversationId: number): Ticket[] {
    return db.value.tickets.filter((ticket) => ticket.conversationId === conversationId)
  }

  function ticketForOrder(orderId: number): Ticket | undefined {
    return ticketsForOrder(orderId)[0]
  }

  function appendMessage(
    draft: DemoDatabase,
    conversation: Conversation,
    senderType: SenderType,
    content: string,
    createdAt = new Date().toISOString(),
  ): ChatMessage {
    const message: ChatMessage = {
      id: nextId(draft.messages),
      conversationId: conversation.id,
      senderType,
      content,
      createdAt,
    }
    draft.messages.push(message)
    conversation.lastMessage = truncate(content, 80)
    conversation.updatedAt = createdAt
    return message
  }

  function createConversation(customerId = DEMO_CUSTOMER_ID): Conversation {
    return clone(
      commit((draft) => {
        const customer = draft.customers.find((item) => item.id === customerId)
        if (!customer) throw new Error('演示客户不存在')

        const now = new Date().toISOString()
        const conversation: Conversation = {
          id: nextId(draft.conversations),
          customerId,
          title: '新的售后咨询',
          status: 'ai',
          agentName: null,
          lastMessage: '',
          createdAt: now,
          updatedAt: now,
          waitingSince: null,
          closedAt: null,
        }
        draft.conversations.push(conversation)
        appendMessage(
          draft,
          conversation,
          'ai',
          buildWelcomeMessage(customer.name),
          now,
        )
        return conversation
      }),
    )
  }

  async function sendCustomerMessage(
    conversationId: number,
    rawContent: string,
  ): Promise<void> {
    const content = rawContent.trim()
    if (!content) return

    const status = commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation) throw new Error('会话不存在')
      if (conversation.status === 'closed') throw new Error('会话已结束，无法继续发送')

      const now = new Date().toISOString()
      const isFirstCustomerMessage = !draft.messages.some(
        (message) =>
          message.conversationId === conversationId &&
          message.senderType === 'customer',
      )
      appendMessage(draft, conversation, 'customer', content, now)

      if (isFirstCustomerMessage && conversation.title === '新的售后咨询') {
        conversation.title = truncate(content, 24)
      }

      return conversation.status
    })

    if (status !== 'ai') return

    typingConversationId.value = conversationId
    await simulateNetworkDelay()

    const shouldTypingClear = typingConversationId.value === conversationId
    if (shouldTypingClear) typingConversationId.value = null

    commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation || conversation.status !== 'ai') return
      appendMessage(draft, conversation, 'ai', buildMockAiReply(content))
    })
  }

  function requestHuman(conversationId: number): void {
    if (typingConversationId.value === conversationId) {
      typingConversationId.value = null
    }

    commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation) throw new Error('会话不存在')
      if (conversation.status !== 'ai') return

      const now = new Date().toISOString()
      conversation.status = 'waiting'
      conversation.waitingSince = now
      appendMessage(
        draft,
        conversation,
        'system',
        '已为您转接人工客服，请稍候。您仍可以继续留言。',
        now,
      )
    })
  }

  function acceptConversation(conversationId: number): void {
    commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation) throw new Error('会话不存在')
      if (conversation.status !== 'waiting') return

      conversation.status = 'human'
      conversation.agentName = DEMO_AGENT_NAME
      conversation.waitingSince = null
      const now = new Date().toISOString()
      appendMessage(draft, conversation, 'system', `${DEMO_AGENT_NAME} 已接入会话。`, now)
    })
  }

  function sendAgentMessage(conversationId: number, rawContent: string): void {
    const content = rawContent.trim()
    if (!content) return

    commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation) throw new Error('会话不存在')
      if (conversation.status !== 'human') {
        throw new Error('请先接入会话，再回复客户')
      }
      appendMessage(draft, conversation, 'agent', content)
    })
  }

  function closeConversation(
    conversationId: number,
    closedBy: 'customer' | 'agent',
  ): void {
    if (typingConversationId.value === conversationId) {
      typingConversationId.value = null
    }

    commit((draft) => {
      const conversation = draft.conversations.find((item) => item.id === conversationId)
      if (!conversation) throw new Error('会话不存在')
      if (conversation.status === 'closed') return

      const now = new Date().toISOString()
      conversation.status = 'closed'
      conversation.closedAt = now
      conversation.waitingSince = null
      appendMessage(
        draft,
        conversation,
        'system',
        closedBy === 'customer' ? '客户已结束本次会话。' : '客服已结束本次会话。',
        now,
      )
    })
  }

  function createTicket(input: CreateTicketInput): Ticket {
    const description = input.description.trim()
    if (!description) throw new Error('请填写问题描述')

    return clone(
      commit((draft) => {
        const order = draft.orders.find((item) => item.id === input.orderId)
        if (!order) throw new Error('关联订单不存在')

        if (input.conversationId) {
          const conversation = draft.conversations.find(
            (item) => item.id === input.conversationId,
          )
          if (!conversation) throw new Error('关联会话不存在')
          if (conversation.customerId !== order.customerId) {
            throw new Error('会话与订单不属于同一客户')
          }
        }

        const now = new Date().toISOString()
        const dateKey = dayjs(now).format('YYYYMMDD')
        const id = nextId(draft.tickets)
        const ticket: Ticket = {
          id,
          ticketNo: `AS${dateKey}${String(id).padStart(4, '0')}`,
          orderId: order.id,
          customerId: order.customerId,
          conversationId: input.conversationId ?? null,
          type: input.type,
          description,
          priority: input.priority,
          status: 'pending',
          assignee: DEMO_AGENT_NAME,
          createdAt: now,
          updatedAt: now,
          resolvedAt: null,
        }
        draft.tickets.push(ticket)
        return ticket
      }),
    )
  }

  function updateTicket(
    ticketId: number,
    patch: Partial<Pick<Ticket, 'priority' | 'assignee' | 'status'>>,
  ): void {
    commit((draft) => {
      const ticket = draft.tickets.find((item) => item.id === ticketId)
      if (!ticket) throw new Error('工单不存在')

      const now = new Date().toISOString()
      if (patch.priority) ticket.priority = patch.priority
      if (patch.assignee) ticket.assignee = patch.assignee
      if (patch.status && patch.status !== ticket.status) {
        ticket.status = patch.status
        if (patch.status === 'resolved') {
          ticket.resolvedAt = now
        } else if (ticket.resolvedAt) {
          ticket.resolvedAt = null
        }
      }
      ticket.updatedAt = now
    })
  }

  function resetDemoData(): void {
    typingConversationId.value = null
    const seeded = createInitialDatabase()
    writeDatabase(seeded)
    db.value = seeded
    notifyOtherTabs()
  }

  return {
    db,
    currentCustomer,
    typingConversationId,
    customerById,
    conversationById,
    messagesFor,
    customerConversations,
    orderById,
    ordersForCustomer,
    ticketById,
    ticketsForOrder,
    ticketsForCustomer,
    ticketsForConversation,
    ticketForOrder,
    createConversation,
    sendCustomerMessage,
    requestHuman,
    acceptConversation,
    sendAgentMessage,
    closeConversation,
    createTicket,
    updateTicket,
    resetDemoData,
  }
})
