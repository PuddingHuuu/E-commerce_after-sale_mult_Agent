from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, UnsignedBigInt


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    ticket_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(
        BigInt,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[int] = mapped_column(
        UnsignedBigInt,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[int | None] = mapped_column(
        BigInt,
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_resolution: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="ai_processing",
        index=True,
    )
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")
    ai_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    feedback_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    feedback_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(
        BigInt,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship()  # noqa: F821
    customer: Mapped["User"] = relationship(foreign_keys=[customer_id])  # noqa: F821
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])  # noqa: F821
    conversation: Mapped["Conversation | None"] = relationship(  # noqa: F821
        back_populates="tickets"
    )
    agent_runs: Mapped[list["TicketAgentRun"]] = relationship(  # noqa: F821
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketAgentRun.sequence",
        lazy="selectin",
    )


class TicketAgentRun(Base):
    __tablename__ = "ticket_agent_runs"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        BigInt,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(32), nullable=False)
    sequence: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    model_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    input_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    ticket: Mapped[Ticket] = relationship(back_populates="agent_runs")
