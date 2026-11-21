from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ConversationStatus, MessageSender, TicketStatus
from app.models import Conversation, ConversationMessage, Merchant, Ticket, User


def add_message(
    db: Session,
    conversation: Conversation,
    sender_type: str,
    content: str,
    sender_id: int | None = None,
) -> ConversationMessage:
    message = ConversationMessage(
        conversation_id=conversation.id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=content.strip(),
        created_at=datetime.now(),
    )
    db.add(message)
    conversation.last_message = content.strip()[:500]
    conversation.updated_at = datetime.now()
    return message


def _find_customer_conversation(db: Session, customer_id: int) -> Conversation | None:
    """Every consumer shares a single platform conversation, regardless of ticket."""
    return db.scalar(
        select(Conversation)
        .where(Conversation.customer_id == customer_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )


def transfer_ticket_to_human(db: Session, ticket: Ticket, reason: str) -> Conversation:
    """Attach a transferred ticket to the consumer's single platform conversation."""
    conversation = _find_customer_conversation(db, ticket.customer_id)
    if conversation is None:
        conversation = ticket.conversation
    if conversation is None:
        conversation = Conversation(
            customer_id=ticket.customer_id,
            order_id=ticket.order_id,
            status=ConversationStatus.WAITING.value,
        )
        db.add(conversation)
        db.flush()
    else:
        conversation.order_id = ticket.order_id
        if conversation.status == ConversationStatus.CLOSED.value:
            # Reopen the same thread for the new issue instead of creating a second dialog.
            conversation.status = ConversationStatus.WAITING.value
            conversation.closed_at = None
            conversation.assigned_agent_id = None
            conversation.merchant_id = None
            conversation.merchant_invited_at = None
            conversation.merchant_invited_by = None

    ticket.conversation_id = conversation.id
    if conversation.status == ConversationStatus.HUMAN.value:
        ticket.status = TicketStatus.HUMAN_PROCESSING.value
        ticket.assignee_id = conversation.assigned_agent_id
    else:
        ticket.status = TicketStatus.WAITING_HUMAN.value
        ticket.assignee_id = None
    ticket.escalation_reason = reason
    ticket.updated_at = datetime.now()

    order = ticket.order
    if order is not None:
        order.after_sale_status = "processing"

    # Keep ticket numbers and AI internal analysis out of the shared chat stream.
    # Merchants may join the conversation later and must not see ticket data.
    add_message(
        db,
        conversation,
        MessageSender.SYSTEM.value,
        "AI 已完成初步处理，已转接人工客服继续为您服务。",
    )
    return conversation


def accept_conversation(
    db: Session,
    conversation: Conversation,
    platform_user: User,
) -> Conversation:
    if conversation.status == ConversationStatus.CLOSED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="会话已结束")

    if conversation.status != ConversationStatus.HUMAN.value:
        conversation.status = ConversationStatus.HUMAN.value
        conversation.assigned_agent_id = platform_user.id
        conversation.updated_at = datetime.now()
        linked_tickets = db.scalars(
            select(Ticket).where(
                Ticket.conversation_id == conversation.id,
                Ticket.status == TicketStatus.WAITING_HUMAN.value,
            )
        ).all()
        for ticket in linked_tickets:
            ticket.status = TicketStatus.HUMAN_PROCESSING.value
            ticket.assignee_id = platform_user.id
            ticket.updated_at = datetime.now()
        add_message(
            db,
            conversation,
            MessageSender.SYSTEM.value,
            f"{platform_user.display_name} 已接入会话。",
        )
    return conversation


def close_conversation(db: Session, conversation: Conversation, actor: User | None = None) -> None:
    conversation.status = ConversationStatus.CLOSED.value
    conversation.closed_at = datetime.now()
    conversation.updated_at = datetime.now()
    linked_tickets = db.scalars(
        select(Ticket).where(
            Ticket.conversation_id == conversation.id,
            Ticket.status.in_(
                [
                    TicketStatus.WAITING_HUMAN.value,
                    TicketStatus.HUMAN_PROCESSING.value,
                ]
            ),
        )
    ).all()
    for ticket in linked_tickets:
        ticket.status = TicketStatus.CLOSED.value
        ticket.updated_at = datetime.now()
    add_message(
        db,
        conversation,
        MessageSender.SYSTEM.value,
        f"{actor.display_name if actor else '客服'} 已结束本次会话。",
        sender_id=actor.id if actor else None,
    )


def invite_merchant(
    db: Session,
    conversation: Conversation,
    merchant: Merchant,
    platform_user: User,
) -> None:
    if conversation.status == ConversationStatus.CLOSED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="会话已结束")
    if merchant.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商家不可用")

    conversation.merchant_id = merchant.id
    conversation.merchant_invited_at = datetime.now()
    conversation.merchant_invited_by = platform_user.id
    conversation.updated_at = datetime.now()
    add_message(
        db,
        conversation,
        MessageSender.SYSTEM.value,
        f"平台客服已邀请「{merchant.store_name}」加入会话。",
        sender_id=platform_user.id,
    )
