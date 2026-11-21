from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.agents.orchestrator import process_ticket
from app.api.deps import AuthContext, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.ticket import (
    TicketCreateRequest,
    TicketFeedbackRequest,
    TicketFeedbackResponse,
    TicketOut,
)
from app.services import ticket_service
from app.services.serializers import serialize_ticket

router = APIRouter(prefix="/buyer/tickets", tags=["消费者-售后"])
buyer_only = require_roles(Role.CONSUMER)


@router.post("", response_model=TicketOut, status_code=202)
def create_ticket(
    payload: TicketCreateRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> TicketOut:
    ticket = ticket_service.create_ticket(db, auth.user.id, payload)
    background_tasks.add_task(process_ticket, ticket.id)
    ticket_out = serialize_ticket(ticket)
    return ticket_out.model_copy(update={"agent_runs": []})


@router.get("", response_model=Page[TicketOut])
def list_tickets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> Page[TicketOut]:
    return ticket_service.list_buyer_tickets(
        db,
        auth.user.id,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> TicketOut:
    return ticket_service.get_buyer_ticket(db, auth.user.id, ticket_id)


@router.post("/{ticket_id}/feedback", response_model=TicketFeedbackResponse)
def submit_feedback(
    ticket_id: int,
    payload: TicketFeedbackRequest,
    auth: AuthContext = Depends(buyer_only),
    db: Session = Depends(get_db),
) -> TicketFeedbackResponse:
    ticket, conversation_id = ticket_service.feedback_ticket(
        db,
        auth.user.id,
        ticket_id,
        payload,
    )
    return TicketFeedbackResponse(ticket=ticket, conversation_id=conversation_id)
