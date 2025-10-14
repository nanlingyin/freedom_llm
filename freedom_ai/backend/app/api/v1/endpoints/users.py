"""
用户相关API端点
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from app.db.session import get_db
from app.services.user_service import get_user_service

router = APIRouter()


class UserProfileUpdate(BaseModel):
    """用户画像更新模型"""
    profile: Dict


class UserPreferencesUpdate(BaseModel):
    """用户偏好更新模型"""
    preferences: Dict


@router.get("/{username}")
async def get_user(username: str, db: Session = Depends(get_db)):
    """
    获取用户信息
    
    Args:
        username: 用户名
        db: 数据库会话
        
    Returns:
        用户信息
    """
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(username)
    
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "profile": user.profile,
        "preferences": user.preferences,
        "is_online": user.is_online,
        "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
        "created_at": user.created_at.isoformat()
    }


@router.put("/{username}/profile")
async def update_profile(
    username: str,
    update: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户画像
    
    Args:
        username: 用户名
        update: 更新数据
        db: 数据库会话
        
    Returns:
        操作结果
    """
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(username)
    
    updated_user = user_service.update_user_profile(user.id, update.profile)
    
    return {
        "success": True,
        "message": "用户画像更新成功",
        "profile": updated_user.profile
    }


@router.put("/{username}/preferences")
async def update_preferences(
    username: str,
    update: UserPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户偏好
    
    Args:
        username: 用户名
        update: 更新数据
        db: 数据库会话
        
    Returns:
        操作结果
    """
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(username)
    
    updated_user = user_service.update_user_preferences(user.id, update.preferences)
    
    return {
        "success": True,
        "message": "用户偏好更新成功",
        "preferences": updated_user.preferences
    }
