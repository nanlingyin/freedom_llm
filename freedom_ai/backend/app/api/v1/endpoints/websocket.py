"""
WebSocket端点 - 实时通信
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.db.session import get_db
from app.services.chat_service import get_chat_service
from app.services.user_service import get_user_service
from app.core.logging import app_logger
import json

router = APIRouter()

# 存储活跃的WebSocket连接
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/chat/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    """
    WebSocket聊天端点
    
    Args:
        websocket: WebSocket连接
        username: 用户名
    """
    await websocket.accept()
    active_connections[username] = websocket
    app_logger.info(f"WebSocket连接建立: {username}")
    
    # 获取数据库会话（注意：WebSocket中使用数据库需要特殊处理）
    from app.db.database import SessionLocal
    db = SessionLocal()
    
    try:
        # 获取或创建用户
        user_service = get_user_service(db)
        user = user_service.get_or_create_user(username)
        user_service.set_user_online_status(user.id, True)
        
        # 发送欢迎消息
        await websocket.send_json({
            "type": "system",
            "content": f"欢迎回来，{user.nickname or username}！",
            "timestamp": None
        })
        
        # 持续接收和处理消息
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue
            
            # 处理聊天
            chat_service = get_chat_service(db)
            result = await chat_service.chat(
                user_id=user.id,
                user_message=user_message,
                stream=False
            )
            
            # 发送AI回复
            if result.get("success"):
                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": result.get("content"),
                    "message_id": result.get("message_id"),
                    "timestamp": result.get("timestamp")
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "content": result.get("error", "处理失败"),
                    "timestamp": None
                })
    
    except WebSocketDisconnect:
        app_logger.info(f"WebSocket连接断开: {username}")
        if username in active_connections:
            del active_connections[username]
        
        # 更新用户离线状态
        user_service.set_user_online_status(user.id, False)
    
    except Exception as e:
        app_logger.error(f"WebSocket错误: {str(e)}")
        await websocket.close()
        if username in active_connections:
            del active_connections[username]
    
    finally:
        db.close()


async def send_proactive_message(username: str, message: str):
    """
    向用户发送主动消息
    
    Args:
        username: 用户名
        message: 消息内容
    """
    if username in active_connections:
        websocket = active_connections[username]
        try:
            await websocket.send_json({
                "type": "proactive",
                "role": "assistant",
                "content": message,
                "timestamp": None
            })
            app_logger.info(f"发送主动消息给 {username}")
        except Exception as e:
            app_logger.error(f"发送主动消息失败: {str(e)}")
