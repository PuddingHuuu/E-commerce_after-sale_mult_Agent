from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.ticket import PlatformTicketUpdateRequest, TicketAdminOut
from app.services import ticket_service

router = APIRouter(prefix="/platform/tickets", tags=["平台-工单"])
platform_only = require_roles(Role.PLATFORM)


@router.get("", response_model=Page[TicketAdminOut])
def list_tickets(
    group: str = Query(default="ai"),
    ticket_status: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> Page[TicketAdminOut]:
    return ticket_service.platform_tickets_page(
        db,
        group=group,
        status_filter=ticket_status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=TicketAdminOut)
def get_ticket(
    ticket_id: int,
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> TicketAdminOut:
    return ticket_service.get_platform_ticket(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketAdminOut)
def update_ticket(
    ticket_id: int,
    payload: PlatformTicketUpdateRequest,
    auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> TicketAdminOut:
    return ticket_service.update_platform_ticket(db, ticket_id, payload.status, auth.user)
