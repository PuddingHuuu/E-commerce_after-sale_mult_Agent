from fastapi import HTTPException, status
from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from app.core.constants import ORDER_TABS
from app.models import Order, OrderItem, Ticket, User
from app.schemas.common import Page
from app.schemas.order import OrderAdminOut, OrderOut
from app.services.serializers import serialize_admin_order, serialize_order


def _apply_keyword(stmt, keyword: str | None):
    if not keyword:
        return stmt
    term = f"%{keyword.strip()}%"
    return stmt.where(
        or_(
            Order.order_no.ilike(term),
            Order.receiver_name.ilike(term),
            Order.receiver_phone.ilike(term),
            Order.items.any(OrderItem.product_name.ilike(term)),
        )
    )


def _buyer_ticket_exists():
    return exists().where(Ticket.order_id == Order.id)


def buyer_orders_page(
    db: Session,
    user_id: int,
    *,
    tab: str,
    keyword: str | None,
    page: int,
    page_size: int,
) -> Page[OrderOut]:
    base = select(Order).where(Order.user_id == user_id)
    base = _apply_keyword(base, keyword)

    counts: dict[str, int] = {}
    for tab_key, statuses in ORDER_TABS.items():
        count_stmt = select(func.count()).select_from(Order).where(
            Order.user_id == user_id,
            Order.order_status.in_(statuses),
        )
        if tab_key == "after_sale":
            count_stmt = (
                select(func.count(func.distinct(Order.id)))
                .select_from(Order)
                .where(
                    Order.user_id == user_id,
                    or_(Order.order_status == "refunding", _buyer_ticket_exists()),
                )
            )
        counts[tab_key] = db.scalar(count_stmt) or 0
    counts["all"] = db.scalar(
        select(func.count()).select_from(Order).where(Order.user_id == user_id)
    ) or 0

    if tab and tab != "all":
        if tab == "after_sale":
            base = base.where(
                or_(Order.order_status == "refunding", _buyer_ticket_exists())
            )
        elif tab in ORDER_TABS:
            base = base.where(Order.order_status.in_(ORDER_TABS[tab]))

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    orders = db.scalars(
        base.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return Page[OrderOut](
        items=[serialize_order(order) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
        counts=counts,
    )


def get_buyer_order(db: Session, user_id: int, order_id: int) -> OrderOut:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return serialize_order(order)


def platform_orders_page(
    db: Session,
    *,
    keyword: str | None,
    order_status: str | None,
    page: int,
    page_size: int,
) -> Page[OrderAdminOut]:
    base = select(Order)
    if keyword:
        term = f"%{keyword.strip()}%"
        base = (
            base.outerjoin(User, User.id == Order.user_id)
            .where(
                or_(
                    Order.order_no.ilike(term),
                    User.display_name.ilike(term),
                    User.phone.ilike(term),
                    Order.receiver_phone.ilike(term),
                    Order.items.any(OrderItem.product_name.ilike(term)),
                )
            )
        )
    if order_status:
        base = base.where(Order.order_status == order_status)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    orders = db.scalars(
        base.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return Page[OrderAdminOut](
        items=[serialize_admin_order(db, order) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_platform_order(db: Session, order_id: int) -> OrderAdminOut:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return serialize_admin_order(db, order)
