"""
聊天相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.services.chat_service import get_chat_service
from app.services.user_service import get_user_service

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    username: str
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool
    content: Optional[str] = None
    message_id: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    发送聊天消息
    
    Args:
        request: 聊天请求
        db: 数据库会话
        
    Returns:
        AI的回复
    """
    try:
        # 获取或创建用户
        user_service = get_user_service(db)
        user = user_service.get_or_create_user(request.username)
        
        # 处理聊天
        chat_service = get_chat_service(db)
        result = await chat_service.chat(
            user_id=user.id,
            user_message=request.message,
            stream=request.stream
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    username: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取聊天历史
    
    Args:
        username: 用户名
        limit: 返回数量
        offset: 偏移量
        db: 数据库会话
        
    Returns:
        聊天历史列表
    """
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(username)
    
    chat_service = get_chat_service(db)
    history = await chat_service.get_chat_history(
        user_id=user.id,
        limit=limit,
        offset=offset
    )
    
    return {
        "success": True,
        "messages": history,
        "count": len(history)
    }


@router.delete("/history")
async def clear_history(username: str, db: Session = Depends(get_db)):
    """
    清除聊天历史
    
    Args:
        username: 用户名
        db: 数据库会话
        
    Returns:
        操作结果
    """
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(username)
    
    chat_service = get_chat_service(db)
    await chat_service.clear_chat_history(user.id)
    
    return {"success": True, "message": "聊天历史已清除"}
