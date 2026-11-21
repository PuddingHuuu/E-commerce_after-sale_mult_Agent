from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.constants import ConversationStatus
from app.models import Conversation, ConversationMessage, Merchant, Order, Ticket, User
from app.schemas.common import Page
from app.schemas.conversation import (
    ConversationDetailOut,
    ConversationSummaryOut,
    LinkedTicketOut,
    MessageOut,
)
from app.services.conversation_service import add_message
from app.services.serializers import serialize_conversation, serialize_message


def merchant_for_user(db: Session, user_id: int) -> Merchant:
    merchant = db.scalar(select(Merchant).where(Merchant.user_id == user_id))
    if merchant is None or merchant.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="商家资料不存在")
    return merchant


def get_conversation_or_404(db: Session, conversation_id: int) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return conversation


def require_customer_conversation(db: Session, customer_id: int, conversation_id: int) -> Conversation:
    conversation = get_conversation_or_404(db, conversation_id)
    if conversation.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return conversation


def require_merchant_conversation(
    db: Session,
    merchant: Merchant,
    conversation_id: int,
) -> Conversation:
    conversation = get_conversation_or_404(db, conversation_id)
    if conversation.merchant_id != merchant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该会话")
    return conversation


def _counts(conversations: list[Conversation]) -> dict[str, int]:
    counts = {
        ConversationStatus.WAITING.value: 0,
        ConversationStatus.HUMAN.value: 0,
        ConversationStatus.CLOSED.value: 0,
        "all": len(conversations),
    }
    for conversation in conversations:
        counts[conversation.status] = counts.get(conversation.status, 0) + 1
    return counts


def buyer_conversations(
    db: Session,
    customer_id: int,
    *,
    keyword: str | None,
    page: int,
    page_size: int,
) -> Page[ConversationSummaryOut]:
    base = select(Conversation).where(Conversation.customer_id == customer_id)
    if keyword:
        term = f"%{keyword.strip()}%"
        linked_order_conversations = (
            select(Ticket.conversation_id)
            .join(Order, Order.id == Ticket.order_id)
            .where(
                Ticket.conversation_id.is_not(None),
                Order.order_no.ilike(term),
            )
        )
        base = base.outerjoin(Order, Order.id == Conversation.order_id).where(
            or_(
                Conversation.last_message.ilike(term),
                Order.order_no.ilike(term),
                Conversation.id.in_(linked_order_conversations),
            )
        )
    all_conversations = db.scalars(base).all()
    total = len(all_conversations)
    conversations = sorted(all_conversations, key=lambda item: item.updated_at, reverse=True)
    conversations = conversations[(page - 1) * page_size : page * page_size]
    return Page[ConversationSummaryOut](
        items=[serialize_conversation(db, conversation) for conversation in conversations],
        total=total,
        page=page,
        page_size=page_size,
        counts=_counts(all_conversations),
    )


def platform_conversations_page(
    db: Session,
    *,
    conversation_status: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
) -> Page[ConversationSummaryOut]:
    base = select(Conversation)
    if conversation_status and conversation_status != "all":
        base = base.where(Conversation.status == conversation_status)
    if keyword:
        term = f"%{keyword.strip()}%"
        linked_order_conversations = (
            select(Ticket.conversation_id)
            .join(Order, Order.id == Ticket.order_id)
            .where(
                Ticket.conversation_id.is_not(None),
                Order.order_no.ilike(term),
            )
        )
        base = (
            base.outerjoin(User, User.id == Conversation.customer_id)
            .outerjoin(Order, Order.id == Conversation.order_id)
            .outerjoin(Merchant, Merchant.id == Conversation.merchant_id)
            .where(
                or_(
                    Conversation.last_message.ilike(term),
                    User.display_name.ilike(term),
                    User.phone.ilike(term),
                    Order.order_no.ilike(term),
                    Merchant.store_name.ilike(term),
                    Conversation.id.in_(linked_order_conversations),
                )
            )
        )
    all_conversations = db.scalars(base).all()
    total = len(all_conversations)
    all_for_counts = all_conversations
    conversations = sorted(all_conversations, key=lambda item: item.updated_at, reverse=True)
    conversations = conversations[(page - 1) * page_size : page * page_size]
    return Page[ConversationSummaryOut](
        items=[
            serialize_conversation(db, conversation, include_tickets=True)
            for conversation in conversations
        ],
        total=total,
        page=page,
        page_size=page_size,
        counts=_counts(all_for_counts),
    )


def merchant_conversations_page(
    db: Session,
    merchant: Merchant,
    *,
    keyword: str | None,
    page: int,
    page_size: int,
) -> Page[ConversationSummaryOut]:
    base = select(Conversation).where(Conversation.merchant_id == merchant.id)
    if keyword:
        term = f"%{keyword.strip()}%"
        base = base.outerjoin(User, User.id == Conversation.customer_id).where(
            or_(
                Conversation.last_message.ilike(term),
                User.display_name.ilike(term),
            )
        )
    all_conversations = db.scalars(base).all()
    total = len(all_conversations)
    conversations = sorted(all_conversations, key=lambda item: item.updated_at, reverse=True)
    conversations = conversations[(page - 1) * page_size : page * page_size]
    return Page[ConversationSummaryOut](
        items=[
            serialize_conversation(db, conversation, for_merchant=True, include_tickets=False)
            for conversation in conversations
        ],
        total=total,
        page=page,
        page_size=page_size,
        counts=_counts(all_conversations),
    )


def _linked_tickets(db: Session, conversation_id: int) -> list[LinkedTicketOut]:
    tickets = db.scalars(
        select(Ticket).where(Ticket.conversation_id == conversation_id).order_by(Ticket.id)
    ).all()
    return [
        LinkedTicketOut(
            id=ticket.id,
            ticket_no=ticket.ticket_no,
            subject=ticket.subject,
            status=ticket.status,
            category=ticket.category,
            updated_at=ticket.updated_at,
        )
        for ticket in tickets
    ]


def conversation_messages(
    db: Session,
    conversation: Conversation,
    *,
    after_id: int = 0,
) -> list[MessageOut]:
    stmt = (
        select(ConversationMessage)
        .where(
            ConversationMessage.conversation_id == conversation.id,
            ConversationMessage.id > after_id,
        )
        .order_by(ConversationMessage.created_at, ConversationMessage.id)
    )
    messages = db.scalars(stmt).all()
    return [serialize_message(db, message, conversation) for message in messages]


def conversation_detail(
    db: Session,
    conversation: Conversation,
    *,
    for_merchant: bool = False,
) -> ConversationDetailOut:
    messages = conversation_messages(db, conversation)
    return ConversationDetailOut(
        conversation=serialize_conversation(
            db,
            conversation,
            for_merchant=for_merchant,
            include_tickets=not for_merchant,
        ),
        messages=messages,
        linked_tickets=[] if for_merchant else _linked_tickets(db, conversation.id),
    )


def send_conversation_message(
    db: Session,
    conversation: Conversation,
    *,
    sender_type: str,
    sender_id: int,
    content: str,
) -> MessageOut:
    if conversation.status == ConversationStatus.CLOSED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="会话已结束")
    if sender_type in {"platform", "merchant"} and conversation.status != ConversationStatus.HUMAN.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="请先接入会话")
    message = add_message(db, conversation, sender_type, content, sender_id)
    db.commit()
    db.refresh(message)
    return serialize_message(db, message, conversation)
