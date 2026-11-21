from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.order import OrderAdminOut
from app.services import order_service

router = APIRouter(prefix="/platform/orders", tags=["平台-订单"])
platform_only = require_roles(Role.PLATFORM)


@router.get("", response_model=Page[OrderAdminOut])
def list_orders(
    keyword: str | None = Query(default=None),
    order_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> Page[OrderAdminOut]:
    return order_service.platform_orders_page(
        db,
        keyword=keyword,
        order_status=order_status,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderAdminOut)
def get_order(
    order_id: int,
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> OrderAdminOut:
    return order_service.get_platform_order(db, order_id)
