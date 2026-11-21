from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import MessageSender, Role
from app.db.session import get_db
from app.models import Merchant
from app.schemas.common import Page
from app.schemas.conversation import (
    ConversationDetailOut,
    ConversationSummaryOut,
    InviteMerchantRequest,
    InviteMerchantResponse,
    MessageOut,
    SendMessageRequest,
)
from app.services import conversation_query_service
from app.services.conversation_service import (
    accept_conversation,
    close_conversation,
    invite_merchant,
)
from app.services.serializers import serialize_conversation, serialize_merchant

router = APIRouter(prefix="/platform/conversations", tags=["平台-会话"])
platform_only = require_roles(Role.PLATFORM)


@router.get("", response_model=Page[ConversationSummaryOut])
def list_conversations(
    conversation_status: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> Page[ConversationSummaryOut]:
    return conversation_query_service.platform_conversations_page(
        db,
        conversation_status=conversation_status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(
    conversation_id: int,
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> ConversationDetailOut:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    return conversation_query_service.conversation_detail(db, conversation)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: int,
    after_id: int = Query(default=0, ge=0),
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> list[MessageOut]:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    return conversation_query_service.conversation_messages(db, conversation, after_id=after_id)


@router.post("/{conversation_id}/accept", response_model=ConversationSummaryOut)
def accept(
    conversation_id: int,
    auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> ConversationSummaryOut:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    accept_conversation(db, conversation, auth.user)
    db.commit()
    db.refresh(conversation)
    return serialize_conversation(db, conversation)


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    payload: SendMessageRequest,
    auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> MessageOut:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    return conversation_query_service.send_conversation_message(
        db,
        conversation,
        sender_type=MessageSender.PLATFORM.value,
        sender_id=auth.user.id,
        content=payload.content,
    )


@router.post("/{conversation_id}/invite-merchant", response_model=InviteMerchantResponse)
def invite(
    conversation_id: int,
    payload: InviteMerchantRequest,
    auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> InviteMerchantResponse:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    merchant = db.get(Merchant, payload.merchant_id)
    if merchant is None or merchant.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")
    if conversation.merchant_id == merchant.id:
        return InviteMerchantResponse(
            conversation=serialize_conversation(db, conversation),
            merchant=serialize_merchant(merchant),
        )
    invite_merchant(db, conversation, merchant, auth.user)
    db.commit()
    db.refresh(conversation)
    return InviteMerchantResponse(
        conversation=serialize_conversation(db, conversation),
        merchant=serialize_merchant(merchant),
    )


@router.post("/{conversation_id}/close", response_model=ConversationSummaryOut)
def close(
    conversation_id: int,
    auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> ConversationSummaryOut:
    conversation = conversation_query_service.get_conversation_or_404(db, conversation_id)
    close_conversation(db, conversation, auth.user)
    db.commit()
    db.refresh(conversation)
    return serialize_conversation(db, conversation)
