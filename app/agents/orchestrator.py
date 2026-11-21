import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.agents.llm_client import llm_client
from app.agents.rules import build_fallback_reply, classify_by_rules
from app.core.config import settings
from app.core.constants import TICKET_CATEGORY_LABELS, TicketStatus
from app.db.session import SessionLocal
from app.models import Order, Ticket, TicketAgentRun
from app.services.conversation_service import transfer_ticket_to_human

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
CLASSIFICATION_PROMPT = (PROMPT_DIR / "classification.md").read_text(encoding="utf-8")
REPLY_PROMPT = (PROMPT_DIR / "reply.md").read_text(encoding="utf-8")
PROMPT_VERSION = "v1"

ORDER_STATUS_LABELS = {
    "pending_payment": "待付款",
    "pending_shipment": "待发货",
    "shipped": "交易中",
    "received": "待评价",
    "completed": "已完成",
    "cancelled": "已取消",
    "refunding": "退款中",
}


def _now_text(value: datetime | None) -> str | None:
    return value.strftime("%Y-%m-%d %H:%M") if value else None


def _add_run(
    db: Session,
    ticket: Ticket,
    agent_name: str,
    sequence: int,
    status: str,
    output: dict[str, Any] | None = None,
    input_data: dict[str, Any] | None = None,
    model_name: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    duration_ms: int | None = None,
    error_message: str | None = None,
) -> TicketAgentRun:
    run = TicketAgentRun(
        ticket_id=ticket.id,
        agent_name=agent_name,
        sequence=sequence,
        status=status,
        model_name=model_name,
        prompt_version=PROMPT_VERSION,
        input_json=input_data,
        output_json=output,
        error_message=error_message,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration_ms=duration_ms,
    )
    db.add(run)
    return run


def _order_facts(order: Order) -> dict[str, Any]:
    items = [
        {
            "name": item.product_name,
            "spec": item.sku_spec,
            "quantity": item.quantity,
            "pay_amount": f"{item.pay_amount:.2f}",
        }
        for item in order.items
    ]
    return {
        "order_no": order.order_no,
        "order_status": order.order_status,
        "order_status_label": ORDER_STATUS_LABELS.get(order.order_status, order.order_status),
        "payment_status": order.payment_status,
        "shipping_status": order.shipping_status,
        "goods_amount": f"{order.goods_amount:.2f}",
        "payable_amount": f"{order.payable_amount:.2f}",
        "paid_amount": f"{order.paid_amount:.2f}",
        "created_at": _now_text(order.created_at),
        "paid_at": _now_text(order.paid_at),
        "shipped_at": _now_text(order.shipped_at),
        "received_at": _now_text(order.received_at),
        "product_names": [item["name"] for item in items],
        "items": items,
        "logistics": {
            "company": order.logistics_company,
            "tracking_no": order.tracking_no,
        }
        if order.logistics_company or order.tracking_no
        else None,
    }


def _validate_classification(data: dict[str, Any]) -> dict[str, Any]:
    category = str(data.get("category", "")).strip()
    if category not in TICKET_CATEGORY_LABELS:
        raise ValueError(f"分类结果不在允许范围内: {category}")
    confidence = float(data.get("confidence", 0))
    if not 0 <= confidence <= 1:
        raise ValueError("置信度必须在 0 到 1 之间")
    steps = data.get("steps", [])
    if not isinstance(steps, list) or not all(isinstance(step, str) for step in steps):
        raise ValueError("处理步骤格式不正确")
    return {
        "category": category,
        "confidence": confidence,
        "steps": steps,
        "need_human": bool(data.get("need_human", False)),
        "reason": str(data.get("reason") or ""),
    }


def _classify(ticket: Ticket, order: Order) -> dict[str, Any]:
    payload = {
        "description": ticket.description,
        "expected_resolution": ticket.expected_resolution,
        "order": {
            "order_no": order.order_no,
            "order_status": order.order_status,
            "product_names": [item.product_name for item in order.items],
        },
    }
    if llm_client.available:
        try:
            result = llm_client.chat_json(
                CLASSIFICATION_PROMPT,
                json.dumps(payload, ensure_ascii=False),
            )
            validated = _validate_classification(result.data)
            return {
                "result": validated,
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "duration_ms": result.duration_ms,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001 - fall back to deterministic rules
            logger.warning("Classification LLM failed, using fallback: %s", exc)
            if not settings.llm_fallback_enabled:
                raise
            fallback = classify_by_rules(ticket.description, ticket.expected_resolution)
            return {
                "result": fallback,
                "model": "rule-fallback",
                "prompt_tokens": None,
                "completion_tokens": None,
                "duration_ms": None,
                "error": str(exc),
            }

    if not settings.llm_fallback_enabled:
        raise RuntimeError("LLM 未配置且规则降级已关闭")

    fallback = classify_by_rules(ticket.description, ticket.expected_resolution)
    return {
        "result": fallback,
        "model": "rule-fallback",
        "prompt_tokens": None,
        "completion_tokens": None,
        "duration_ms": None,
        "error": None,
    }


def _retrieve(ticket: Ticket, order: Order) -> tuple[dict[str, Any] | None, str | None]:
    if not order.items:
        return None, "订单没有商品明细"
    facts = _order_facts(order)
    # A logistics issue without any logistics information cannot be resolved automatically.
    if ticket.category == "logistics" and not facts.get("logistics"):
        return facts, "订单缺少物流公司或运单号"
    return facts, None


def _reply(
    ticket: Ticket,
    order: Order,
    classification: dict[str, Any],
    facts: dict[str, Any],
) -> dict[str, Any]:
    if llm_client.available:
        payload = {
            "classification": classification,
            "facts": facts,
            "user_description": ticket.description,
        }
        try:
            result = llm_client.chat_json(REPLY_PROMPT, json.dumps(payload, ensure_ascii=False))
            reply = result.data.get("reply")
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("回复 Agent 未返回有效回复")
            return {
                "result": {
                    "reply": reply.strip(),
                    "need_human": bool(result.data.get("need_human", False)),
                    "reason": str(result.data.get("reason") or ""),
                },
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "duration_ms": result.duration_ms,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Reply LLM failed, using fallback: %s", exc)
            if not settings.llm_fallback_enabled:
                raise
            fallback = build_fallback_reply(classification["category"], order, facts)
            return {
                "result": fallback,
                "model": "rule-fallback",
                "prompt_tokens": None,
                "completion_tokens": None,
                "duration_ms": None,
                "error": str(exc),
            }

    if not settings.llm_fallback_enabled:
        raise RuntimeError("LLM 未配置且规则降级已关闭")

    fallback = build_fallback_reply(classification["category"], order, facts)
    return {
        "result": fallback,
        "model": "rule-fallback",
        "prompt_tokens": None,
        "completion_tokens": None,
        "duration_ms": None,
        "error": None,
    }


def _handoff(
    db: Session,
    ticket: Ticket,
    reason: str,
    *,
    category: str | None = None,
    confidence: float | None = None,
) -> None:
    ticket.status = TicketStatus.WAITING_HUMAN.value
    ticket.updated_at = datetime.now()
    if category:
        ticket.category = category
    if confidence is not None:
        ticket.confidence = confidence
    transfer_ticket_to_human(db, ticket, reason)
    _add_run(
        db,
        ticket,
        "handoff",
        4,
        "success",
        output={"reason": reason},
        input_data={"ticket_no": ticket.ticket_no},
    )


def _process_with_session(ticket_id: int) -> None:
    with SessionLocal() as db:
        ticket = db.get(Ticket, ticket_id)
        if ticket is None:
            return
        if ticket.status != TicketStatus.AI_PROCESSING.value:
            return
        order = db.get(Order, ticket.order_id)
        if order is None:
            _handoff(db, ticket, "关联订单不存在")
            db.commit()
            return

        # 1. Classification Agent
        classification_result = _classify(ticket, order)
        classification = classification_result["result"]
        _add_run(
            db,
            ticket,
            "classification",
            1,
            "fallback" if classification_result["error"] else "success",
            output=classification,
            input_data={
                "description": ticket.description,
                "expected_resolution": ticket.expected_resolution,
                "order_no": order.order_no,
            },
            model_name=classification_result["model"],
            prompt_tokens=classification_result["prompt_tokens"],
            completion_tokens=classification_result["completion_tokens"],
            duration_ms=classification_result["duration_ms"],
            error_message=classification_result["error"],
        )

        category = classification["category"]
        confidence = classification["confidence"]
        ticket.category = category
        ticket.confidence = confidence

        if classification["need_human"]:
            _handoff(
                db,
                ticket,
                classification["reason"] or "分类 Agent 无法自动判断",
                category=category,
                confidence=confidence,
            )
            db.commit()
            return
        if confidence < settings.ai_confidence_threshold:
            _handoff(
                db,
                ticket,
                f"分类置信度 {confidence:.2f} 低于阈值 {settings.ai_confidence_threshold:.2f}",
                category=category,
                confidence=confidence,
            )
            db.commit()
            return

        # 2. Data Retrieval Agent
        retrieval_started = time.perf_counter()
        facts, retrieval_error = _retrieve(ticket, order)
        _add_run(
            db,
            ticket,
            "retrieval",
            2,
            "failed" if retrieval_error else "success",
            output=facts or {},
            input_data={"order_id": order.id, "order_no": order.order_no},
            model_name="database",
            duration_ms=int((time.perf_counter() - retrieval_started) * 1000),
            error_message=retrieval_error,
        )
        if retrieval_error or facts is None:
            _handoff(db, ticket, retrieval_error or "数据检索失败", category=category, confidence=confidence)
            db.commit()
            return

        # 3. Reply Agent
        reply_result = _reply(ticket, order, classification, facts)
        reply = reply_result["result"]
        _add_run(
            db,
            ticket,
            "reply",
            3,
            "fallback" if reply_result["error"] else "success",
            output=reply,
            input_data={"classification": classification, "facts": facts},
            model_name=reply_result["model"],
            prompt_tokens=reply_result["prompt_tokens"],
            completion_tokens=reply_result["completion_tokens"],
            duration_ms=reply_result["duration_ms"],
            error_message=reply_result["error"],
        )

        if reply["need_human"]:
            _handoff(
                db,
                ticket,
                reply["reason"] or "回复 Agent 认为信息不足",
                category=category,
                confidence=confidence,
            )
            db.commit()
            return

        ticket.ai_reply = reply["reply"]
        ticket.ai_result_json = {
            "category": category,
            "confidence": confidence,
            "steps": classification.get("steps", []),
            "facts": {
                "order_no": facts.get("order_no"),
                "order_status": facts.get("order_status"),
                "product_names": facts.get("product_names"),
            },
            "reply": reply["reply"],
            "model": reply_result["model"],
        }
        ticket.status = TicketStatus.AWAITING_FEEDBACK.value
        ticket.updated_at = datetime.now()
        order.after_sale_status = "processing"
        db.commit()


def _safe_handoff(ticket_id: int, reason: str) -> None:
    try:
        with SessionLocal() as db:
            ticket = db.get(Ticket, ticket_id)
            if ticket is None or ticket.status != TicketStatus.AI_PROCESSING.value:
                return
            _add_run(
                db,
                ticket,
                "handoff",
                4,
                "failed",
                output={"reason": reason},
                input_data={"ticket_id": ticket_id},
                error_message=reason,
            )
            _handoff(db, ticket, reason)
            db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("Failed to mark ticket %s as human handoff", ticket_id)


def process_ticket(ticket_id: int) -> None:
    """Run the three-agent pipeline. Intended to be executed in a background task."""
    try:
        _process_with_session(ticket_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent pipeline failed for ticket %s", ticket_id)
        _safe_handoff(ticket_id, f"AI 处理异常：{exc}")
