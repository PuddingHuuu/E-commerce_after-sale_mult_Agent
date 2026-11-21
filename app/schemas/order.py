from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class OrderItemOut(ORMModel):
    id: int
    product_id: int | None = None
    sku_id: str | None = None
    product_name: str
    sku_spec: str | None = None
    unit_price: Decimal
    quantity: int
    item_amount: Decimal
    discount_amount: Decimal
    pay_amount: Decimal
    refund_quantity: int = 0
    refund_amount: Decimal = Decimal("0.00")


class OrderSummaryOut(BaseModel):
    id: int
    order_no: str
    product_name: str
    product_spec: str | None = None


class OrderOut(ORMModel):
    id: int
    order_no: str
    user_id: int
    shop_id: int
    order_status: str
    payment_status: str
    shipping_status: str
    after_sale_status: str
    currency: str
    goods_amount: Decimal
    discount_amount: Decimal
    freight_amount: Decimal
    payable_amount: Decimal
    paid_amount: Decimal
    refund_amount: Decimal
    payment_method: str | None = None
    order_source: str
    buyer_note: str | None = None
    cancel_reason: str | None = None
    receiver_name: str
    receiver_phone: str
    receiver_city: str | None = None
    receiver_address: str | None = None
    logistics_company: str | None = None
    tracking_no: str | None = None
    item_count: int
    paid_at: datetime | None = None
    shipped_at: datetime | None = None
    received_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []


class OrderAdminOut(OrderOut):
    customer_name: str | None = None
    customer_phone: str | None = None
    ticket_count: int = 0
    latest_ticket_no: str | None = None
    latest_ticket_status: str | None = None
