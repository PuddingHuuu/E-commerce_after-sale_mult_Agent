from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.order import OrderSummaryOut


class TicketCreateRequest(BaseModel):
    order_id: int
    description: str = Field(min_length=10, max_length=2000)
    expected_resolution: str | None = Field(default=None, max_length=500)


class TicketFeedbackRequest(BaseModel):
    satisfied: bool
    reason: str | None = Field(default=None, max_length=500)


class TicketFeedbackResponse(BaseModel):
    ticket: "TicketOut"
    conversation_id: int | None = None


class AgentRunOut(ORMModel):
    id: int
    agent_name: str
    sequence: int
    status: str
    model_name: str | None = None
    prompt_version: str | None = None
    input_json: dict[str, Any] | None = None
    output_json: dict[str, Any] | None = None
    error_message: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    duration_ms: int | None = None
    created_at: datetime


class TicketOrderOut(BaseModel):
    id: int
    order_no: str
    order_status: str
    product_name: str
    product_spec: str | None = None
    amount: str | None = None


class TicketOut(BaseModel):
    id: int
    ticket_no: str
    subject: str
    description: str
    expected_resolution: str | None = None
    category: str | None = None
    confidence: float | None = None
    status: str
    priority: str
    ai_reply: str | None = None
    ai_result_json: dict[str, Any] | None = None
    escalation_reason: str | None = None
    feedback_result: str | None = None
    feedback_reason: str | None = None
    conversation_id: int | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    order: TicketOrderOut | None = None
    agent_runs: list[AgentRunOut] = []


class TicketAdminOut(TicketOut):
    customer_id: int
    customer_name: str
    customer_phone: str | None = None
    assignee_id: int | None = None
    assignee_name: str | None = None
    linked_conversation_status: str | None = None


class PlatformTicketUpdateRequest(BaseModel):
    status: str


class TicketSummaryOut(BaseModel):
    ai_processing: int
    awaiting_feedback: int
    waiting_human: int
    human_processing: int
    resolved: int
    closed: int


TicketFeedbackResponse.model_rebuild()
