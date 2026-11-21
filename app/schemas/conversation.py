from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ConversationSummaryOut(BaseModel):
    id: int
    status: str
    customer_id: int
    customer_name: str
    order_id: int | None = None
    order_no: str | None = None
    order_product: str | None = None
    assigned_agent_name: str | None = None
    merchant_id: int | None = None
    merchant_name: str | None = None
    last_message: str | None = None
    ticket_numbers: list[str] = []
    created_at: datetime
    updated_at: datetime


class MessageOut(ORMModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_id: int | None = None
    sender_name: str | None = None
    content: str
    created_at: datetime


class LinkedTicketOut(BaseModel):
    id: int
    ticket_no: str
    subject: str
    status: str
    category: str | None = None
    updated_at: datetime


class ConversationDetailOut(BaseModel):
    conversation: ConversationSummaryOut
    messages: list[MessageOut] = []
    linked_tickets: list[LinkedTicketOut] = []


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class InviteMerchantRequest(BaseModel):
    merchant_id: int


class MerchantOptionOut(BaseModel):
    id: int
    store_name: str
    contact_name: str | None = None
    phone: str | None = None


class InviteMerchantResponse(BaseModel):
    conversation: ConversationSummaryOut
    merchant: MerchantOptionOut
