from enum import StrEnum


class Role(StrEnum):
    CONSUMER = "consumer"
    PLATFORM = "platform"
    MERCHANT = "merchant"


class TicketStatus(StrEnum):
    AI_PROCESSING = "ai_processing"
    AWAITING_FEEDBACK = "awaiting_feedback"
    WAITING_HUMAN = "waiting_human"
    HUMAN_PROCESSING = "human_processing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ConversationStatus(StrEnum):
    WAITING = "waiting"
    HUMAN = "human"
    CLOSED = "closed"


class MessageSender(StrEnum):
    CUSTOMER = "customer"
    PLATFORM = "platform"
    MERCHANT = "merchant"
    SYSTEM = "system"


class TicketGroup(StrEnum):
    AI = "ai"
    HUMAN = "human"
    ENDED = "ended"


TICKET_GROUP_STATUSES: dict[TicketGroup, tuple[str, ...]] = {
    TicketGroup.AI: (TicketStatus.AI_PROCESSING, TicketStatus.AWAITING_FEEDBACK),
    TicketGroup.HUMAN: (TicketStatus.WAITING_HUMAN, TicketStatus.HUMAN_PROCESSING),
    TicketGroup.ENDED: (TicketStatus.RESOLVED, TicketStatus.CLOSED),
}

TICKET_STATUS_GROUP: dict[str, TicketGroup] = {
    status: group
    for group, statuses in TICKET_GROUP_STATUSES.items()
    for status in statuses
}

ORDER_TABS: dict[str, tuple[str, ...]] = {
    "pending_payment": ("pending_payment",),
    "pending_shipment": ("pending_shipment",),
    "shipped": ("shipped",),
    "received": ("received",),
    "completed": ("completed",),
    "after_sale": ("refunding",),
    "cancelled": ("cancelled",),
}

TICKET_CATEGORY_LABELS: dict[str, str] = {
    "refund_only": "仅退款",
    "return_refund": "退货退款",
    "exchange": "换货",
    "repair": "维修",
    "logistics": "物流异常",
    "other": "其他问题",
}

AFTER_SALE_STEPS: dict[str, list[str]] = {
    "refund_only": ["核对订单状态与支付信息", "确认是否符合仅退款条件", "引导用户提交售后申请"],
    "return_refund": ["核对订单签收时间", "确认商品状态与售后政策", "引导用户提交退货退款申请"],
    "exchange": ["核对商品规格与库存", "确认换货条件", "引导用户提交换货申请"],
    "repair": ["确认商品故障表现", "核对保修状态", "引导用户提交维修申请"],
    "logistics": ["核对物流公司与运单号", "确认最近物流节点", "必要时转人工核实"],
    "other": ["补充确认问题信息", "结合订单和售后政策判断", "必要时转人工处理"],
}
