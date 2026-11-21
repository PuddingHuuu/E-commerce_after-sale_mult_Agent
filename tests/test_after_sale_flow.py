from datetime import datetime, timedelta

from app.core.config import settings


def test_auth_sessions_and_role_isolation(client, auth_headers):
    me = client.get("/api/v1/auth/me", headers=auth_headers["consumer"])
    assert me.status_code == 200
    assert me.json()["user"]["role"] == "consumer"

    login = client.post(
        "/api/v1/auth/login",
        json={
            "role": "consumer",
            "login_name": "13812345678",
            "password": "Demo1234",
            "remember": True,
        },
    )
    assert login.status_code == 200
    expires_at = datetime.fromisoformat(login.json()["expires_at"])
    assert expires_at > datetime.now() + timedelta(days=2)

    buyer_orders = client.get("/api/v1/buyer/orders?tab=all&page=1&page_size=5", headers=auth_headers["consumer"])
    assert buyer_orders.status_code == 200
    assert buyer_orders.json()["total"] == 50
    assert buyer_orders.json()["counts"]["all"] == 50

    platform_orders = client.get("/api/v1/platform/orders", headers=auth_headers["platform"])
    assert platform_orders.status_code == 200
    assert platform_orders.json()["total"] == 50

    buyer_on_platform = client.get("/api/v1/platform/tickets", headers=auth_headers["consumer"])
    assert buyer_on_platform.status_code == 403

    merchant_on_platform = client.get("/api/v1/platform/tickets", headers=auth_headers["merchant"])
    assert merchant_on_platform.status_code == 403


def test_ticket_agents_feedback_handoff_and_merchant_isolation(client, auth_headers):
    completed = client.get(
        "/api/v1/buyer/orders?tab=completed&page=1&page_size=5",
        headers=auth_headers["consumer"],
    )
    assert completed.status_code == 200
    order_id = completed.json()["items"][0]["id"]

    created = client.post(
        "/api/v1/buyer/tickets",
        headers=auth_headers["consumer"],
        json={
            "order_id": order_id,
            "description": "商品存在质量问题，设备故障无法正常使用，申请维修处理。",
            "expected_resolution": "维修",
        },
    )
    assert created.status_code == 202, created.text
    ticket_id = created.json()["id"]

    ticket = client.get(f"/api/v1/buyer/tickets/{ticket_id}", headers=auth_headers["consumer"])
    assert ticket.status_code == 200
    payload = ticket.json()
    assert payload["status"] == "awaiting_feedback"
    assert payload["category"] == "repair"
    assert payload["agent_runs"] == []  # internal traces are not exposed to consumers

    platform_ticket = client.get(
        f"/api/v1/platform/tickets/{ticket_id}",
        headers=auth_headers["platform"],
    )
    assert platform_ticket.status_code == 200
    assert [run["agent_name"] for run in platform_ticket.json()["agent_runs"]] == [
        "classification",
        "retrieval",
        "reply",
    ]

    feedback = client.post(
        f"/api/v1/buyer/tickets/{ticket_id}/feedback",
        headers=auth_headers["consumer"],
        json={"satisfied": False, "reason": "AI 没有解决我的问题"},
    )
    assert feedback.status_code == 200
    conversation_id = feedback.json()["conversation_id"]
    assert conversation_id
    assert feedback.json()["ticket"]["status"] in {"waiting_human", "human_processing"}

    accept = client.post(
        f"/api/v1/platform/conversations/{conversation_id}/accept",
        headers=auth_headers["platform"],
    )
    assert accept.status_code == 200
    assert accept.json()["status"] == "human"

    sent = client.post(
        f"/api/v1/platform/conversations/{conversation_id}/messages",
        headers=auth_headers["platform"],
        json={"content": "您好，我来协助处理这个问题。"},
    )
    assert sent.status_code == 200
    assert sent.json()["sender_type"] == "platform"

    merchant_list = client.get("/api/v1/platform/merchants", headers=auth_headers["platform"])
    assert merchant_list.status_code == 200
    merchant_id = merchant_list.json()[0]["id"]

    invite = client.post(
        f"/api/v1/platform/conversations/{conversation_id}/invite-merchant",
        headers=auth_headers["platform"],
        json={"merchant_id": merchant_id},
    )
    assert invite.status_code == 200

    merchant_conversations = client.get(
        "/api/v1/merchant/conversations",
        headers=auth_headers["merchant"],
    )
    assert merchant_conversations.status_code == 200
    assert merchant_conversations.json()["total"] >= 1

    merchant_detail = client.get(
        f"/api/v1/merchant/conversations/{conversation_id}",
        headers=auth_headers["merchant"],
    )
    assert merchant_detail.status_code == 200
    merchant_payload = merchant_detail.json()
    assert merchant_payload["linked_tickets"] == []
    assert merchant_payload["conversation"]["ticket_numbers"] == []
    assert merchant_payload["conversation"]["order_no"] is None
    assert "工单" not in str(merchant_payload)

    forbidden = client.get("/api/v1/platform/tickets", headers=auth_headers["merchant"])
    assert forbidden.status_code == 403

    merchant_message = client.post(
        f"/api/v1/merchant/conversations/{conversation_id}/messages",
        headers=auth_headers["merchant"],
        json={"content": "这里是商家客服，我来协助处理。"},
    )
    assert merchant_message.status_code == 200
    assert merchant_message.json()["sender_type"] == "merchant"

    messages = client.get(
        f"/api/v1/buyer/conversations/{conversation_id}/messages",
        headers=auth_headers["consumer"],
    )
    assert messages.status_code == 200
    assert any(
        item["content"] == "您好，我来协助处理这个问题。" for item in messages.json()
    )
    assert any(
        item["content"] == "这里是商家客服，我来协助处理。" for item in messages.json()
    )


def test_vague_ticket_auto_handoff(client, auth_headers):
    completed = client.get(
        "/api/v1/buyer/orders?tab=completed&page=1&page_size=1",
        headers=auth_headers["consumer"],
    )
    order_id = completed.json()["items"][0]["id"]
    created = client.post(
        "/api/v1/buyer/tickets",
        headers=auth_headers["consumer"],
        json={
            "order_id": order_id,
            "description": "这个订单有点问题，帮我看看怎么处理比较好。",
        },
    )
    assert created.status_code == 202
    ticket = client.get(
        f"/api/v1/buyer/tickets/{created.json()['id']}",
        headers=auth_headers["consumer"],
    )
    assert ticket.status_code == 200
    assert ticket.json()["conversation_id"] is not None
    assert ticket.json()["status"] in {"waiting_human", "human_processing"}
    assert "无法识别" in (ticket.json()["escalation_reason"] or "")


def test_single_platform_conversation_per_consumer(client, auth_headers):
    conversations = client.get(
        "/api/v1/platform/conversations?keyword=林晓",
        headers=auth_headers["platform"],
    )
    assert conversations.status_code == 200
    assert conversations.json()["total"] == 1
    conversation_id = conversations.json()["items"][0]["id"]

    completed = client.get(
        "/api/v1/buyer/orders?tab=completed&page=1&page_size=1",
        headers=auth_headers["consumer"],
    )
    order_id = completed.json()["items"][0]["id"]
    created = client.post(
        "/api/v1/buyer/tickets",
        headers=auth_headers["consumer"],
        json={
            "order_id": order_id,
            "description": "订单商品有划痕，希望安排换货处理，麻烦人工确认。",
            "expected_resolution": "换货",
        },
    )
    assert created.status_code == 202, created.text
    ticket_id = created.json()["id"]

    feedback = client.post(
        f"/api/v1/buyer/tickets/{ticket_id}/feedback",
        headers=auth_headers["consumer"],
        json={"satisfied": False, "reason": "希望平台人工继续处理"},
    )
    assert feedback.status_code == 200
    assert feedback.json()["conversation_id"] == conversation_id

    conversations = client.get(
        "/api/v1/platform/conversations?keyword=林晓",
        headers=auth_headers["platform"],
    )
    assert conversations.status_code == 200
    assert conversations.json()["total"] == 1

    detail = client.get(
        f"/api/v1/platform/conversations/{conversation_id}",
        headers=auth_headers["platform"],
    )
    assert detail.status_code == 200
    linked_ticket_ids = {item["id"] for item in detail.json()["linked_tickets"]}
    assert ticket_id in linked_ticket_ids
    assert len(detail.json()["linked_tickets"]) >= 2


def test_registration_and_platform_invite_code(client):
    import uuid

    suffix = uuid.uuid4().hex[:8]
    consumer_login = f"139{suffix[:8]}"
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "role": "consumer",
            "login_name": consumer_login,
            "password": "NewUser1234",
            "display_name": "新消费者",
            "phone": consumer_login,
        },
    )
    assert registered.status_code == 201, registered.text
    new_token = {"Authorization": f"Bearer {registered.json()['token']}"}
    orders = client.get("/api/v1/buyer/orders", headers=new_token)
    assert orders.status_code == 200
    assert orders.json()["total"] == 0

    wrong_invite = client.post(
        "/api/v1/auth/register",
        json={
            "role": "platform",
            "login_name": f"staff_{suffix}",
            "password": "NewStaff1234",
            "display_name": "新客服",
            "invite_code": "WRONG-CODE",
        },
    )
    assert wrong_invite.status_code == 403

    right_invite = client.post(
        "/api/v1/auth/register",
        json={
            "role": "platform",
            "login_name": f"staff_{suffix}",
            "password": "NewStaff1234",
            "display_name": "新客服",
            "invite_code": settings.platform_register_invite_code,
        },
    )
    assert right_invite.status_code == 201, right_invite.text


def test_platform_search_endpoints(client, auth_headers):
    orders = client.get(
        "/api/v1/platform/orders?keyword=林晓&page=1&page_size=5",
        headers=auth_headers["platform"],
    )
    assert orders.status_code == 200
    assert orders.json()["total"] >= 1

    tickets = client.get(
        "/api/v1/platform/tickets?group=all&keyword=AS-DEMO",
        headers=auth_headers["platform"],
    )
    assert tickets.status_code == 200
    assert tickets.json()["total"] >= 1

    conversations = client.get(
        "/api/v1/platform/conversations?keyword=林晓",
        headers=auth_headers["platform"],
    )
    assert conversations.status_code == 200
    assert conversations.json()["total"] == 1
