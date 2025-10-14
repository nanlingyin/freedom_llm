"""
用户数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from app.db.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))  # 头像URL
    
    # 用户画像信息
    profile = Column(JSON, default={})  # 存储用户的各种属性
    preferences = Column(JSON, default={})  # 用户偏好
    
    # 活跃时间统计
    active_hours = Column(JSON, default=[])  # 记录用户活跃的时间段
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserEmotion(Base):
    """用户情感记录表"""
    __tablename__ = "user_emotions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 情感维度评分 (0-10)
    happy = Column(Integer, default=5)
    sad = Column(Integer, default=0)
    anxious = Column(Integer, default=0)
    angry = Column(Integer, default=0)
    excited = Column(Integer, default=0)
    
    # 主要情感
    primary_emotion = Column(String(20))
    
    # 来源消息
    message_id = Column(Integer)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserEmotion(user_id={self.user_id}, primary={self.primary_emotion})>"
