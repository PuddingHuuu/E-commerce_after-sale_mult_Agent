from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.constants import AFTER_SALE_STEPS, TICKET_CATEGORY_LABELS
from app.models import Order

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "return_refund": ("退货退款", "退货", "寄回", "七天无理由", "无理由退", "退掉"),
    "refund_only": ("仅退款", "退钱", "退款", "不想要", "钱退"),
    "exchange": ("换货", "换新", "尺码", "颜色", "型号", "买错"),
    "repair": ("维修", "坏了", "故障", "杂音", "漏水", "破损", "质量问题", "开不了机", "无法使用"),
    "logistics": ("物流", "快递", "没收到", "未收到", "发货", "运单", "配送", "签收", "物流不动"),
}


def classify_by_rules(
    description: str,
    expected_resolution: str | None,
) -> dict[str, Any]:
    text = f"{description} {expected_resolution or ''}".strip()
    if any(word in text for word in ("转人工", "人工客服", "人工处理")):
        return {
            "category": "other",
            "confidence": 0.4,
            "steps": AFTER_SALE_STEPS["other"],
            "need_human": True,
            "reason": "用户主动要求人工处理",
        }

    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for keyword in keywords if keyword in text)

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_category, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if top_score == 0:
        return {
            "category": "other",
            "confidence": 0.35,
            "steps": AFTER_SALE_STEPS["other"],
            "need_human": True,
            "reason": "无法识别明确的售后类型",
        }

    # return_refund is a more specific form of refund. Prefer it when both appear.
    if scores.get("return_refund", 0) > 0:
        top_category = "return_refund"
        top_score = scores["return_refund"]
        second_score = max(
            (score for category, score in scores.items() if category != "return_refund"),
            default=0,
        )

    confidence = min(0.95, 0.62 + top_score * 0.1)
    if second_score and abs(top_score - second_score) <= 0:
        confidence = min(confidence, 0.55)

    return {
        "category": top_category,
        "confidence": round(confidence, 2),
        "steps": AFTER_SALE_STEPS[top_category],
        "need_human": confidence < 0.65,
        "reason": "问题类型存在多个可能" if confidence < 0.65 else "",
    }


def build_fallback_reply(
    category: str,
    order: Order,
    facts: dict[str, Any],
) -> dict[str, Any]:
    product_name = facts.get("product_names", ["商品"])[0]
    order_status = facts.get("order_status", order.order_status)
    steps = AFTER_SALE_STEPS.get(category, AFTER_SALE_STEPS["other"])
    logistics = facts.get("logistics") or {}
    logistics_text = ""
    if logistics.get("company") or logistics.get("tracking_no"):
        logistics_text = (
            f"当前物流信息：{logistics.get('company') or '承运商未提供'}，"
            f"运单号 {logistics.get('tracking_no') or '暂无'}。"
        )

    intro_map = {
        "refund_only": "已收到您的退款咨询。",
        "return_refund": "已收到您的退货退款咨询。",
        "exchange": "已收到您的换货咨询。",
        "repair": "已收到您的维修/质量问题反馈。",
        "logistics": "已收到您的物流问题反馈。",
        "other": "已收到您的售后咨询。",
    }
    category_label = TICKET_CATEGORY_LABELS.get(category, "售后问题")
    step_text = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, 1))
    reply = (
        f"{intro_map.get(category, '已收到您的售后咨询。')}\n\n"
        f"售后类型：{category_label}\n"
        f"关联商品：{product_name}\n"
        f"当前订单状态：{facts.get('order_status_label') or order_status}\n"
        f"{logistics_text}\n\n"
        f"建议处理步骤：\n{step_text}\n\n"
        "以上为 AI 根据当前订单信息生成的初步处理建议，"
        "不会自动执行退款或换货操作。如对结果不满意，可以转人工继续处理。"
    ).replace("\n\n\n", "\n\n")
    return {"reply": reply.strip(), "need_human": False, "reason": ""}


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def amount_text(value: Decimal | None) -> str:
    return f"{Decimal(value or 0):.2f}"
