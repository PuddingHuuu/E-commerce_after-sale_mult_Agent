import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Conversation,
    ConversationMessage,
    Merchant,
    Order,
    OrderItem,
    Ticket,
    TicketAgentRun,
    User,
)

DEMO_CUSTOMER_ID = 10001
DEMO_PLATFORM_ID = 20001
DEMO_MERCHANT_USER_ID = 30001
DEMO_MERCHANT_ID = 1
DEMO_CUSTOMER_LOGIN = "13812345678"
DEMO_PLATFORM_LOGIN = "agent01"
DEMO_MERCHANT_LOGIN = "merchant01"
DEMO_PASSWORD = "Demo1234"
DEMO_PLATFORM_PASSWORD = "Platform1234"
DEMO_MERCHANT_PASSWORD = "Merchant1234"

SEED_ORDERS_PATH = Path(__file__).resolve().parents[2] / "database" / "orders_seed_data.json"


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _ensure_users(db: Session) -> tuple[User, User, Merchant]:
    customer = db.scalar(select(User).where(User.role == "consumer", User.login_name == DEMO_CUSTOMER_LOGIN))
    platform = db.scalar(select(User).where(User.role == "platform", User.login_name == DEMO_PLATFORM_LOGIN))
    merchant_user = db.scalar(select(User).where(User.role == "merchant", User.login_name == DEMO_MERCHANT_LOGIN))

    if customer is None:
        customer = User(
            id=DEMO_CUSTOMER_ID,
            role="consumer",
            login_name=DEMO_CUSTOMER_LOGIN,
            password_hash=hash_password(DEMO_PASSWORD),
            display_name="林晓",
            phone="13812345678",
            status="active",
        )
        db.add(customer)
        db.flush()

    if platform is None:
        platform = User(
            id=DEMO_PLATFORM_ID,
            role="platform",
            login_name=DEMO_PLATFORM_LOGIN,
            password_hash=hash_password(DEMO_PLATFORM_PASSWORD),
            display_name="客服小橙",
            phone="13900001111",
            status="active",
        )
        db.add(platform)
        db.flush()

    if merchant_user is None:
        merchant_user = User(
            id=DEMO_MERCHANT_USER_ID,
            role="merchant",
            login_name=DEMO_MERCHANT_LOGIN,
            password_hash=hash_password(DEMO_MERCHANT_PASSWORD),
            display_name="陈商家",
            phone="13911112222",
            status="active",
        )
        db.add(merchant_user)
        db.flush()

    merchant = db.scalar(select(Merchant).where(Merchant.user_id == merchant_user.id))
    if merchant is None:
        merchant = Merchant(
            id=DEMO_MERCHANT_ID,
            user_id=merchant_user.id,
            store_name="橙心优选官方旗舰店",
            contact_name="陈商家",
            phone="13911112222",
            status="active",
        )
        db.add(merchant)
        db.flush()

    return customer, platform, merchant


def _seed_orders_if_empty(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Order)) > 0:
        return
    if not SEED_ORDERS_PATH.exists():
        return

    payload = json.loads(SEED_ORDERS_PATH.read_text(encoding="utf-8"))
    for raw in payload["orders"]:
        order = Order(
            id=raw["id"],
            order_no=raw["order_no"],
            user_id=raw["user_id"],
            shop_id=raw["shop_id"],
            order_status=raw["order_status"],
            payment_status=raw["payment_status"],
            shipping_status=raw["shipping_status"],
            after_sale_status=raw["after_sale_status"],
            currency=raw["currency"],
            goods_amount=Decimal(raw["goods_amount"]),
            discount_amount=Decimal(raw["discount_amount"]),
            freight_amount=Decimal(raw["freight_amount"]),
            payable_amount=Decimal(raw["payable_amount"]),
            paid_amount=Decimal(raw["paid_amount"]),
            refund_amount=Decimal(raw["refund_amount"]),
            payment_method=raw["payment_method"],
            order_source=raw["order_source"],
            buyer_note=raw["buyer_note"],
            cancel_reason=raw["cancel_reason"],
            receiver_name=raw["receiver_name"],
            receiver_phone=raw["receiver_phone"],
            receiver_province=raw["receiver_province"],
            receiver_city=raw["receiver_city"],
            receiver_district=raw["receiver_district"],
            receiver_address=raw["receiver_address"],
            logistics_company=raw["logistics_company"],
            tracking_no=raw["tracking_no"],
            item_count=raw["item_count"],
            paid_at=_parse_dt(raw["paid_at"]),
            shipped_at=_parse_dt(raw["shipped_at"]),
            received_at=_parse_dt(raw["received_at"]),
            completed_at=_parse_dt(raw["completed_at"]),
            cancelled_at=_parse_dt(raw["cancelled_at"]),
            created_at=_parse_dt(raw["created_at"]) or datetime.now(),
            updated_at=_parse_dt(raw["updated_at"]) or datetime.now(),
            version=raw.get("version", 0),
        )
        for item_raw in raw["items"]:
            order.items.append(
                OrderItem(
                    id=item_raw["id"],
                    product_id=item_raw.get("product_id"),
                    sku_id=item_raw.get("sku_id"),
                    product_name=item_raw["product_name"],
                    sku_spec=item_raw.get("sku_spec"),
                    unit_price=Decimal(item_raw["unit_price"]),
                    quantity=item_raw["quantity"],
                    item_amount=Decimal(item_raw["item_amount"]),
                    discount_amount=Decimal(item_raw["discount_amount"]),
                    pay_amount=Decimal(item_raw["pay_amount"]),
                    refund_quantity=item_raw.get("refund_quantity", 0),
                    refund_amount=Decimal(item_raw.get("refund_amount", "0.00")),
                    created_at=_parse_dt(item_raw["created_at"]) or datetime.now(),
                )
            )
        db.add(order)
    db.flush()


def _agent_run(
    agent_name: str,
    sequence: int,
    output: dict[str, Any],
    duration_ms: int = 120,
) -> TicketAgentRun:
    return TicketAgentRun(
        agent_name=agent_name,
        sequence=sequence,
        status="success",
        model_name="rule-fallback",
        prompt_version="v1",
        input_json={},
        output_json=output,
        duration_ms=duration_ms,
    )


def _seed_demo_tickets_if_empty(
    db: Session,
    customer: User,
    platform: User,
    merchant: Merchant,
) -> None:
    if db.scalar(select(func.count()).select_from(Ticket)) > 0:
        return

    eligible_orders = db.scalars(
        select(Order)
        .where(Order.user_id == customer.id)
        .order_by(Order.id)
        .limit(8)
    ).all()
    if len(eligible_orders) < 3:
        return

    now = datetime.now()

    ai_order = eligible_orders[0]
    transfer_order = eligible_orders[1]
    human_order = eligible_orders[2]
    resolved_order = eligible_orders[3] if len(eligible_orders) > 3 else eligible_orders[0]

    ai_ticket = Ticket(
        ticket_no="AS-DEMO-0001",
        customer_id=customer.id,
        order_id=ai_order.id,
        subject="商品使用问题售后",
        description="商品使用过程中出现异常，希望平台协助确认是否可以退货处理。",
        category="return_refund",
        confidence=0.88,
        status="awaiting_feedback",
        priority="normal",
        ai_reply=(
            "经核对订单信息，您的订单目前符合售后登记条件。"
            "建议先查看商品状态，保留商品与包装，并根据页面提示提交退货申请。"
            "如对结果有疑问，可以转人工由平台客服进一步核实。"
        ),
        ai_result_json={
            "category": "return_refund",
            "steps": ["核对订单状态", "确认商品状态", "引导提交退货申请"],
            "retrieval_summary": "订单与商品信息已核对",
        },
        created_at=now - timedelta(hours=6),
        updated_at=now - timedelta(hours=5, minutes=55),
    )
    ai_ticket.agent_runs.extend(
        [
            _agent_run("classification", 1, {"category": "return_refund", "confidence": 0.88}, 88),
            _agent_run("retrieval", 2, {"order_status": ai_order.order_status}, 42),
            _agent_run("reply", 3, {"need_human": False}, 120),
        ]
    )
    ai_order.after_sale_status = "processing"

    transfer_ticket = Ticket(
        ticket_no="AS-DEMO-0002",
        customer_id=customer.id,
        order_id=transfer_order.id,
        subject="订单物流异常",
        description="订单显示已发货，但物流多日没有更新，希望人工核实。",
        category="logistics",
        confidence=0.91,
        status="waiting_human",
        priority="high",
        ai_reply="已为您整理订单物流信息，建议转人工进一步核实。",
        ai_result_json={
            "category": "logistics",
            "steps": ["核对物流单号", "核实物流节点", "等待人工跟进"],
            "retrieval_summary": "物流状态需要人工确认",
        },
        escalation_reason="用户对物流结果不满意，申请转人工",
        created_at=now - timedelta(hours=4),
        updated_at=now - timedelta(hours=2, minutes=40),
    )
    transfer_ticket.agent_runs.extend(
        [
            _agent_run("classification", 1, {"category": "logistics", "confidence": 0.91}, 100),
            _agent_run("retrieval", 2, {"logistics_company": transfer_order.logistics_company}, 55),
            _agent_run("reply", 3, {"need_human": True}, 140),
        ]
    )
    transfer_order.after_sale_status = "processing"

    transfer_conversation = Conversation(
        customer_id=customer.id,
        order_id=transfer_order.id,
        status="waiting",
        last_message="AI 已完成初步处理，等待人工客服接入。",
        created_at=now - timedelta(hours=2, minutes=40),
        updated_at=now - timedelta(hours=2, minutes=40),
    )
    transfer_ticket.conversation = transfer_conversation
    transfer_conversation.messages.extend(
        [
            ConversationMessage(
                sender_type="system",
                content="AI 已完成初步处理，因物流问题需要人工核实，已为您转接人工客服。",
                created_at=now - timedelta(hours=2, minutes=40),
            ),
            ConversationMessage(
                sender_type="customer",
                sender_id=customer.id,
                content="麻烦帮我确认一下物流到底到哪里了，谢谢。",
                created_at=now - timedelta(hours=2, minutes=35),
            ),
        ]
    )
    transfer_conversation.last_message = "麻烦帮我确认一下物流到底到哪里了，谢谢。"

    human_ticket = Ticket(
        ticket_no="AS-DEMO-0003",
        customer_id=customer.id,
        order_id=human_order.id,
        subject="商品尺码换货",
        description="收到的商品尺码不合适，希望申请换货。",
        category="exchange",
        confidence=0.86,
        status="human_processing",
        priority="normal",
        ai_reply="商品支持换货，已为您登记需求并转人工处理。",
        ai_result_json={
            "category": "exchange",
            "steps": ["确认商品状态", "登记换货", "平台客服跟进"],
            "retrieval_summary": "订单信息完整",
        },
        escalation_reason="用户主动申请人工处理",
        assignee_id=platform.id,
        created_at=now - timedelta(days=1, hours=3),
        updated_at=now - timedelta(hours=3),
    )
    human_ticket.agent_runs.extend(
        [
            _agent_run("classification", 1, {"category": "exchange", "confidence": 0.86}, 95),
            _agent_run("retrieval", 2, {"order_status": human_order.order_status}, 48),
            _agent_run("reply", 3, {"need_human": True}, 130),
        ]
    )
    human_order.after_sale_status = "processing"

    human_conversation = Conversation(
        customer_id=customer.id,
        order_id=human_order.id,
        status="human",
        assigned_agent_id=platform.id,
        merchant_id=merchant.id,
        merchant_invited_at=now - timedelta(hours=4),
        merchant_invited_by=platform.id,
        last_message="您好，这里是商家客服，我来协助处理换货。",
        created_at=now - timedelta(days=1, hours=3),
        updated_at=now - timedelta(hours=3),
    )
    human_ticket.conversation = human_conversation
    human_conversation.messages.extend(
        [
            ConversationMessage(
                sender_type="system",
                content="AI 已完成初步处理，已为您转接人工客服。",
                created_at=now - timedelta(days=1, hours=3),
            ),
            ConversationMessage(
                sender_type="system",
                content="客服小橙已接入会话。",
                created_at=now - timedelta(hours=6),
            ),
            ConversationMessage(
                sender_type="platform",
                sender_id=platform.id,
                content="您好，我是平台客服小橙，商家的换货信息我已经帮您同步。",
                created_at=now - timedelta(hours=5, minutes=30),
            ),
            ConversationMessage(
                sender_type="system",
                content="平台客服已邀请「橙心优选官方旗舰店」加入会话。",
                created_at=now - timedelta(hours=4),
            ),
            ConversationMessage(
                sender_type="merchant",
                sender_id=merchant.user_id,
                content="您好，这里是商家客服，我来协助处理换货，请确认商品吊牌是否完整。",
                created_at=now - timedelta(hours=3),
            ),
        ]
    )

    resolved_ticket = Ticket(
        ticket_no="AS-DEMO-0004",
        customer_id=customer.id,
        order_id=resolved_order.id,
        subject="退款申请已处理",
        description="用户申请退款，已由平台客服处理完成。",
        category="refund_only",
        confidence=0.9,
        status="resolved",
        priority="normal",
        ai_reply="退款申请已完成处理。",
        feedback_result="satisfied",
        assignee_id=platform.id,
        created_at=now - timedelta(days=4),
        updated_at=now - timedelta(days=2),
        resolved_at=now - timedelta(days=2),
    )
    resolved_ticket.agent_runs.extend(
        [
            _agent_run("classification", 1, {"category": "refund_only", "confidence": 0.9}, 80),
            _agent_run("retrieval", 2, {"order_status": resolved_order.order_status}, 40),
            _agent_run("reply", 3, {"need_human": True}, 110),
        ]
    )
    resolved_order.after_sale_status = "completed"

    db.add_all([ai_ticket, transfer_ticket, human_ticket, resolved_ticket])
    db.flush()


def seed_demo_data(db: Session) -> None:
    """Seed demo accounts and data once. Safe to call on every startup."""
    customer, platform, merchant = _ensure_users(db)
    _seed_orders_if_empty(db)
    _seed_demo_tickets_if_empty(db, customer, platform, merchant)
    db.commit()
