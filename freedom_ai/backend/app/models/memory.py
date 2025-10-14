"""
记忆数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from app.db.database import Base


class Memory(Base):
    """记忆表（长期记忆）"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 记忆内容
    content = Column(Text, nullable=False)
    category = Column(String(50))  # 记忆分类：personal_info, preference, event, emotion等
    
    # 记忆元数据
    importance = Column(Float, default=0.5)  # 重要性评分 0-1
    access_count = Column(Integer, default=0)  # 访问次数
    
    # 关联信息
    source_message_ids = Column(String(255))  # 来源消息ID
    related_keywords = Column(String(255))  # 相关关键词
    
    # 向量数据库中的ID
    vector_id = Column(String(100), unique=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Memory(id={self.id}, user_id={self.user_id}, category={self.category})>"


class MemoryTag(Base):
    """记忆标签表"""
    __tablename__ = "memory_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, index=True, nullable=False)
    tag = Column(String(50), index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MemoryTag(memory_id={self.memory_id}, tag={self.tag})>"
