"""
消息数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
import enum
from app.db.database import Base


class MessageRole(str, enum.Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    SYSTEM = "system"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 消息内容
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    
    # 消息元数据
    token_count = Column(Integer, default=0)  # token数量
    context_used = Column(Boolean, default=False)  # 是否被用作上下文
    
    # 是否为主动发起的消息
    is_proactive = Column(Boolean, default=False)
    
    # 关联的记忆ID
    related_memory_ids = Column(String(255))  # 逗号分隔的记忆ID
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, user_id={self.user_id})>"


class Conversation(Base):
    """对话会话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 会话信息
    title = Column(String(100))  # 会话标题（可自动生成）
    summary = Column(Text)  # 会话摘要
    
    # 消息计数
    message_count = Column(Integer, default=0)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"
