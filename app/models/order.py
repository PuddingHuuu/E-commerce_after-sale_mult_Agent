from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, UnsignedBigInt


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(UnsignedBigInt, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInt, nullable=False, index=True)
    shop_id: Mapped[int] = mapped_column(BigInt, nullable=False, default=1, index=True)
    order_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    payment_status: Mapped[str] = mapped_column(String(32), nullable=False)
    shipping_status: Mapped[str] = mapped_column(String(32), nullable=False)
    after_sale_status: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CNY")
    goods_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    freight_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    payable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    order_source: Mapped[str] = mapped_column(String(24), nullable=False, default="app")
    buyer_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    receiver_name: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    receiver_province: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_city: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_district: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_address: Mapped[str] = mapped_column(String(255), nullable=False)
    logistics_company: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tracking_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    items: Mapped[list["OrderItem"]] = relationship(  # noqa: F821
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(UnsignedBigInt, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        UnsignedBigInt,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(BigInt, nullable=True)
    sku_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku_spec: Mapped[str | None] = mapped_column(String(200), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    item_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    pay_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    refund_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    order: Mapped[Order] = relationship(back_populates="items")
