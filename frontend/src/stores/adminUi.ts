import { reactive, ref } from 'vue'
import { defineStore } from 'pinia'

interface CreateTicketContext {
  customerId: number | null
  conversationId: number | null
  orderId: number | null
}

export const useAdminUiStore = defineStore('adminUi', () => {
  const orderDrawerVisible = ref(false)
  const selectedOrderId = ref<number | null>(null)
  const ticketDrawerVisible = ref(false)
  const selectedTicketId = ref<number | null>(null)

  const ticketDialog = reactive({
    visible: false,
    customerId: null as number | null,
    conversationId: null as number | null,
    orderId: null as number | null,
  })

  function openOrderDrawer(orderId: number): void {
    selectedOrderId.value = orderId
    orderDrawerVisible.value = true
    ticketDrawerVisible.value = false
  }

  function openTicketDrawer(ticketId: number): void {
    selectedTicketId.value = ticketId
    ticketDrawerVisible.value = true
    orderDrawerVisible.value = false
  }

  function openCreateTicket(context: Partial<CreateTicketContext> = {}): void {
    ticketDialog.customerId = context.customerId ?? null
    ticketDialog.conversationId = context.conversationId ?? null
    ticketDialog.orderId = context.orderId ?? null
    ticketDialog.visible = true
  }

  function closeAll(): void {
    orderDrawerVisible.value = false
    ticketDrawerVisible.value = false
    ticketDialog.visible = false
  }

  return {
    orderDrawerVisible,
    selectedOrderId,
    ticketDrawerVisible,
    selectedTicketId,
    ticketDialog,
    openOrderDrawer,
    openTicketDrawer,
    openCreateTicket,
    closeAll,
  }
})
