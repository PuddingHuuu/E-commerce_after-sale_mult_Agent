from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.order import OrderOut
from app.services import order_service

router = APIRouter(prefix="/buyer/orders", tags=["消费者-订单"])
buyer_only = require_roles(Role.CONSUMER)


@router.get("", response_model=Page[OrderOut])
def list_orders(
    tab: str = Query(default="all"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> Page[OrderOut]:
    return order_service.buyer_orders_page(
        db,
        auth.user.id,
        tab=tab,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> OrderOut:
    return order_service.get_buyer_order(db, auth.user.id, order_id)
