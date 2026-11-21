from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import MessageSender, Role
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.conversation import (
    ConversationDetailOut,
    ConversationSummaryOut,
    MessageOut,
    SendMessageRequest,
)
from app.services import conversation_query_service

router = APIRouter(prefix="/merchant/conversations", tags=["商家-会话"])
merchant_only = require_roles(Role.MERCHANT)


@router.get("", response_model=Page[ConversationSummaryOut])
def list_conversations(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    auth: AuthContext = Depends(merchant_only),
    db: Session = Depends(get_db),
) -> Page[ConversationSummaryOut]:
    merchant = conversation_query_service.merchant_for_user(db, auth.user.id)
    return conversation_query_service.merchant_conversations_page(
        db,
        merchant,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(
    conversation_id: int,
    auth: AuthContext = Depends(merchant_only),
    db: Session = Depends(get_db),
) -> ConversationDetailOut:
    merchant = conversation_query_service.merchant_for_user(db, auth.user.id)
    conversation = conversation_query_service.require_merchant_conversation(
        db, merchant, conversation_id
    )
    return conversation_query_service.conversation_detail(db, conversation, for_merchant=True)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: int,
    after_id: int = Query(default=0, ge=0),
    auth: AuthContext = Depends(merchant_only),
    db: Session = Depends(get_db),
) -> list[MessageOut]:
    merchant = conversation_query_service.merchant_for_user(db, auth.user.id)
    conversation = conversation_query_service.require_merchant_conversation(
        db, merchant, conversation_id
    )
    return conversation_query_service.conversation_messages(db, conversation, after_id=after_id)


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    payload: SendMessageRequest,
    auth: AuthContext = Depends(merchant_only),
    db: Session = Depends(get_db),
) -> MessageOut:
    merchant = conversation_query_service.merchant_for_user(db, auth.user.id)
    conversation = conversation_query_service.require_merchant_conversation(
        db, merchant, conversation_id
    )
    return conversation_query_service.send_conversation_message(
        db,
        conversation,
        sender_type=MessageSender.MERCHANT.value,
        sender_id=auth.user.id,
        content=payload.content,
    )
