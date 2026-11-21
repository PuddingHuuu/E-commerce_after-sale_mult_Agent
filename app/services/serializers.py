from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Conversation,
    ConversationMessage,
    Merchant,
    Order,
    Ticket,
    User,
)
from app.schemas.conversation import (
    ConversationSummaryOut,
    MerchantOptionOut,
    MessageOut,
)
from app.schemas.order import OrderAdminOut, OrderOut, OrderItemOut
from app.schemas.ticket import AgentRunOut, TicketAdminOut, TicketOrderOut, TicketOut


def order_product_text(order: Order) -> tuple[str, str | None]:
    if not order.items:
        return "商品订单", None
    first = order.items[0]
    return first.product_name, first.sku_spec


def serialize_order(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        shop_id=order.shop_id,
        order_status=order.order_status,
        payment_status=order.payment_status,
        shipping_status=order.shipping_status,
        after_sale_status=order.after_sale_status,
        currency=order.currency,
        goods_amount=order.goods_amount,
        discount_amount=order.discount_amount,
        freight_amount=order.freight_amount,
        payable_amount=order.payable_amount,
        paid_amount=order.paid_amount,
        refund_amount=order.refund_amount,
        payment_method=order.payment_method,
        order_source=order.order_source,
        buyer_note=order.buyer_note,
        cancel_reason=order.cancel_reason,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_city=order.receiver_city,
        receiver_address=order.receiver_address,
        logistics_company=order.logistics_company,
        tracking_no=order.tracking_no,
        item_count=order.item_count,
        paid_at=order.paid_at,
        shipped_at=order.shipped_at,
        received_at=order.received_at,
        completed_at=order.completed_at,
        cancelled_at=order.cancelled_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[OrderItemOut.model_validate(item) for item in order.items],
    )


def serialize_admin_order(db: Session, order: Order) -> OrderAdminOut:
    base = serialize_order(order)
    customer = db.get(User, order.user_id)
    tickets = db.scalars(
        select(Ticket).where(Ticket.order_id == order.id).order_by(Ticket.updated_at.desc())
    ).all()
    latest = tickets[0] if tickets else None
    return OrderAdminOut(
        **base.model_dump(),
        customer_name=customer.display_name if customer else None,
        customer_phone=customer.phone if customer else None,
        ticket_count=len(tickets),
        latest_ticket_no=latest.ticket_no if latest else None,
        latest_ticket_status=latest.status if latest else None,
    )


def _ticket_order(order: Order | None) -> TicketOrderOut | None:
    if order is None:
        return None
    name, spec = order_product_text(order)
    return TicketOrderOut(
        id=order.id,
        order_no=order.order_no,
        order_status=order.order_status,
        product_name=name,
        product_spec=spec,
        amount=f"{Decimal(order.payable_amount):.2f}",
    )


def serialize_ticket(ticket: Ticket, order: Order | None = None) -> TicketOut:
    target_order = order or ticket.order
    return TicketOut(
        id=ticket.id,
        ticket_no=ticket.ticket_no,
        subject=ticket.subject,
        description=ticket.description,
        expected_resolution=ticket.expected_resolution,
        category=ticket.category,
        confidence=ticket.confidence,
        status=ticket.status,
        priority=ticket.priority,
        ai_reply=ticket.ai_reply,
        ai_result_json=ticket.ai_result_json,
        escalation_reason=ticket.escalation_reason,
        feedback_result=ticket.feedback_result,
        feedback_reason=ticket.feedback_reason,
        conversation_id=ticket.conversation_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        order=_ticket_order(target_order),
        agent_runs=[AgentRunOut.model_validate(run) for run in ticket.agent_runs],
    )


def serialize_admin_ticket(db: Session, ticket: Ticket) -> TicketAdminOut:
    base = serialize_ticket(ticket)
    customer = db.get(User, ticket.customer_id)
    assignee = db.get(User, ticket.assignee_id) if ticket.assignee_id else None
    conversation = db.get(Conversation, ticket.conversation_id) if ticket.conversation_id else None
    return TicketAdminOut(
        **base.model_dump(),
        customer_id=ticket.customer_id,
        customer_name=customer.display_name if customer else "—",
        customer_phone=customer.phone if customer else None,
        assignee_id=ticket.assignee_id,
        assignee_name=assignee.display_name if assignee else None,
        linked_conversation_status=conversation.status if conversation else None,
    )


def _sender_name(db: Session, message: ConversationMessage, conversation: Conversation) -> str | None:
    if message.sender_type == "customer":
        customer = db.get(User, message.sender_id or conversation.customer_id)
        return customer.display_name if customer else None
    if message.sender_type == "platform":
        platform_user = db.get(User, message.sender_id) if message.sender_id else None
        return platform_user.display_name if platform_user else "平台客服"
    if message.sender_type == "merchant":
        merchant_user = db.get(User, message.sender_id) if message.sender_id else None
        if merchant_user:
            merchant = db.scalar(select(Merchant).where(Merchant.user_id == merchant_user.id))
            return merchant.store_name if merchant else merchant_user.display_name
        return "商家客服"
    return None


def serialize_message(
    db: Session,
    message: ConversationMessage,
    conversation: Conversation,
) -> MessageOut:
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_type=message.sender_type,
        sender_id=message.sender_id,
        sender_name=_sender_name(db, message, conversation),
        content=message.content,
        created_at=message.created_at,
    )


def serialize_conversation(
    db: Session,
    conversation: Conversation,
    *,
    for_merchant: bool = False,
    include_tickets: bool = True,
) -> ConversationSummaryOut:
    customer = db.get(User, conversation.customer_id)
    order = db.get(Order, conversation.order_id) if conversation.order_id else None
    product_name, _ = order_product_text(order) if order else (None, None)
    agent = db.get(User, conversation.assigned_agent_id) if conversation.assigned_agent_id else None
    merchant = db.scalar(select(Merchant).where(Merchant.id == conversation.merchant_id)) if conversation.merchant_id else None
    tickets = db.scalars(
        select(Ticket)
        .where(Ticket.conversation_id == conversation.id)
        .order_by(Ticket.id)
    ).all()

    ticket_numbers = [
        ticket.ticket_no for ticket in tickets
    ] if include_tickets and not for_merchant else []

    return ConversationSummaryOut(
        id=conversation.id,
        status=conversation.status,
        customer_id=conversation.customer_id,
        customer_name=customer.display_name if customer else "消费者",
        order_id=None if for_merchant else conversation.order_id,
        order_no=None if for_merchant else (order.order_no if order else None),
        order_product=None if for_merchant else product_name,
        assigned_agent_name=agent.display_name if agent else None,
        merchant_id=conversation.merchant_id,
        merchant_name=merchant.store_name if merchant else None,
        last_message=conversation.last_message,
        ticket_numbers=ticket_numbers,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def serialize_merchant(merchant: Merchant) -> MerchantOptionOut:
    return MerchantOptionOut(
        id=merchant.id,
        store_name=merchant.store_name,
        contact_name=merchant.contact_name,
        phone=merchant.phone,
    )
