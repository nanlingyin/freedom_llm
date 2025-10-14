"""
API路由聚合
"""
from fastapi import APIRouter
from app.api.v1.endpoints import chat, users, websocket

api_router = APIRouter()

# 注册各个端点路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
