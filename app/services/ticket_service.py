from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.constants import (
    TICKET_GROUP_STATUSES,
    TicketGroup,
    TicketStatus,
)
from app.models import Order, Ticket, User
from app.schemas.common import Page
from app.schemas.ticket import TicketAdminOut, TicketCreateRequest, TicketFeedbackRequest, TicketOut
from app.services.conversation_service import transfer_ticket_to_human
from app.services.serializers import serialize_admin_ticket, serialize_ticket


BUYER_ELIGIBLE_ORDER_STATUSES = (
    "pending_shipment",
    "shipped",
    "received",
    "completed",
    "refunding",
)


def _new_ticket_no(ticket: Ticket, db: Session) -> str:
    db.flush()
    return f"AS{datetime.now():%Y%m%d}{ticket.id:06d}"


def create_ticket(db: Session, customer_id: int, payload: TicketCreateRequest) -> Ticket:
    order = db.get(Order, payload.order_id)
    if order is None or order.user_id != customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.order_status not in BUYER_ELIGIBLE_ORDER_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前订单状态不可申请售后")

    ticket = Ticket(
        ticket_no=f"TMP-{uuid4().hex[:12]}",
        customer_id=customer_id,
        order_id=order.id,
        subject=payload.description.strip()[:60],
        description=payload.description.strip(),
        expected_resolution=payload.expected_resolution.strip() if payload.expected_resolution else None,
        status=TicketStatus.AI_PROCESSING.value,
        priority="normal",
    )
    db.add(ticket)
    db.flush()
    ticket.ticket_no = _new_ticket_no(ticket, db)
    order.after_sale_status = "processing"
    db.commit()
    db.refresh(ticket)
    return ticket


def _buyer_hide_internal_runs(ticket_out: TicketOut) -> TicketOut:
    return ticket_out.model_copy(update={"agent_runs": []})


def get_buyer_ticket(db: Session, customer_id: int, ticket_id: int) -> TicketOut:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="售后单不存在")
    return _buyer_hide_internal_runs(serialize_ticket(ticket))


def list_buyer_tickets(
    db: Session,
    customer_id: int,
    *,
    page: int,
    page_size: int,
) -> Page[TicketOut]:
    base = select(Ticket).where(Ticket.customer_id == customer_id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    tickets = db.scalars(
        base.order_by(Ticket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    counts: dict[str, int] = {}
    for item in TicketStatus:
        counts[item.value] = db.scalar(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.customer_id == customer_id, Ticket.status == item.value)
        ) or 0
    return Page[TicketOut](
        items=[_buyer_hide_internal_runs(serialize_ticket(ticket)) for ticket in tickets],
        total=total,
        page=page,
        page_size=page_size,
        counts=counts,
    )


def feedback_ticket(
    db: Session,
    customer_id: int,
    ticket_id: int,
    payload: TicketFeedbackRequest,
) -> tuple[TicketOut, int | None]:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="售后单不存在")
    if ticket.status != TicketStatus.AWAITING_FEEDBACK.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前售后单不处于待反馈状态")

    ticket.feedback_reason = payload.reason.strip() if payload.reason else None
    conversation_id: int | None = None
    if payload.satisfied:
        ticket.feedback_result = "satisfied"
        ticket.status = TicketStatus.RESOLVED.value
        ticket.resolved_at = datetime.now()
        ticket.updated_at = datetime.now()
        ticket.order.after_sale_status = "completed"
    else:
        ticket.feedback_result = "dissatisfied"
        conversation = transfer_ticket_to_human(
            db,
            ticket,
            payload.reason.strip() if payload.reason else "用户对 AI 处理结果不满意",
        )
        conversation_id = conversation.id
    db.commit()
    db.refresh(ticket)
    return _buyer_hide_internal_runs(serialize_ticket(ticket)), conversation_id


def _ticket_counts(tickets: list[Ticket]) -> dict[str, int]:
    counts = {item.value: 0 for item in TicketStatus}
    for ticket in tickets:
        counts[ticket.status] = counts.get(ticket.status, 0) + 1
    for group, statuses in TICKET_GROUP_STATUSES.items():
        counts[group.value] = sum(1 for ticket in tickets if ticket.status in statuses)
    counts["all"] = len(tickets)
    return counts


def platform_tickets_page(
    db: Session,
    *,
    group: str | None,
    status_filter: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
) -> Page[TicketAdminOut]:
    base = (
        select(Ticket)
        .join(Order, Order.id == Ticket.order_id)
        .join(User, User.id == Ticket.customer_id)
    )
    if keyword:
        term = f"%{keyword.strip()}%"
        base = base.where(
            or_(
                Ticket.ticket_no.ilike(term),
                Ticket.subject.ilike(term),
                Ticket.description.ilike(term),
                Order.order_no.ilike(term),
                User.display_name.ilike(term),
                User.phone.ilike(term),
            )
        )

    matched = list(db.scalars(base.order_by(Ticket.updated_at.desc())).all())
    counts = _ticket_counts(matched)

    if status_filter:
        filtered = [ticket for ticket in matched if ticket.status == status_filter]
    elif group and group != "all":
        try:
            allowed_statuses = set(TICKET_GROUP_STATUSES[TicketGroup(group)])
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法工单分组") from exc
        filtered = [ticket for ticket in matched if ticket.status in allowed_statuses]
    else:
        filtered = matched

    total = len(filtered)
    page_items = filtered[(page - 1) * page_size : page * page_size]
    return Page[TicketAdminOut](
        items=[serialize_admin_ticket(db, ticket) for ticket in page_items],
        total=total,
        page=page,
        page_size=page_size,
        counts=counts,
    )


def get_platform_ticket(db: Session, ticket_id: int) -> TicketAdminOut:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
    return serialize_admin_ticket(db, ticket)


def update_platform_ticket(
    db: Session,
    ticket_id: int,
    new_status: str,
    platform_user: User,
) -> TicketAdminOut:
    if new_status not in {TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持标记已解决或关闭工单",
        )
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在")
    if ticket.status in {TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="工单已结束")

    ticket.status = new_status
    ticket.assignee_id = ticket.assignee_id or platform_user.id
    ticket.updated_at = datetime.now()
    if new_status == TicketStatus.RESOLVED.value:
        ticket.resolved_at = datetime.now()
        ticket.order.after_sale_status = "completed"
    else:
        ticket.order.after_sale_status = "completed"
    db.commit()
    db.refresh(ticket)
    return serialize_admin_ticket(db, ticket)
