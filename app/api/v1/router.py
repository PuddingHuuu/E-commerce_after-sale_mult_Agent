from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    buyer_conversations,
    buyer_orders,
    buyer_tickets,
    merchant_conversations,
    platform_conversations,
    platform_merchants,
    platform_orders,
    platform_tickets,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(buyer_orders.router)
api_router.include_router(buyer_tickets.router)
api_router.include_router(buyer_conversations.router)
api_router.include_router(platform_tickets.router)
api_router.include_router(platform_orders.router)
api_router.include_router(platform_conversations.router)
api_router.include_router(platform_merchants.router)
api_router.include_router(merchant_conversations.router)
