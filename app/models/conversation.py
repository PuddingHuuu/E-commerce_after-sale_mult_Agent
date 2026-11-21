from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, UnsignedBigInt


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        BigInt,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[int | None] = mapped_column(
        UnsignedBigInt,
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="waiting",
        index=True,
    )
    assigned_agent_id: Mapped[int | None] = mapped_column(
        BigInt,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    merchant_id: Mapped[int | None] = mapped_column(
        BigInt,
        ForeignKey("merchants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    merchant_invited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    merchant_invited_by: Mapped[int | None] = mapped_column(
        BigInt,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    customer: Mapped["User"] = relationship(foreign_keys=[customer_id])  # noqa: F821
    assigned_agent: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[assigned_agent_id]
    )
    merchant: Mapped["Merchant | None"] = relationship()  # noqa: F821
    order: Mapped["Order | None"] = relationship()  # noqa: F821
    messages: Mapped[list["ConversationMessage"]] = relationship(  # noqa: F821
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at, ConversationMessage.id",
        lazy="selectin",
    )
    tickets: Mapped[list["Ticket"]] = relationship(  # noqa: F821
        back_populates="conversation",
        lazy="selectin",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInt,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(String(16), nullable=False)
    sender_id: Mapped[int | None] = mapped_column(BigInt, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
