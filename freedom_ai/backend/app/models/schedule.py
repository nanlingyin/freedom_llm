"""
日程数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
import enum
from app.db.database import Base


class ScheduleStatus(str, enum.Enum):
    """日程状态枚举"""
    PENDING = "pending"  # 待处理
    REMINDED = "reminded"  # 已提醒
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class SchedulePriority(str, enum.Enum):
    """日程优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Schedule(Base):
    """日程表"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 日程信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 时间
    schedule_time = Column(DateTime, nullable=False, index=True)
    remind_at = Column(DateTime, index=True)  # 提醒时间
    remind_advance_minutes = Column(Integer, default=15)  # 提前提醒分钟数
    
    # 状态和优先级
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PENDING)
    priority = Column(Enum(SchedulePriority), default=SchedulePriority.MEDIUM)
    
    # 重复设置
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100))  # 重复规则（如：daily, weekly, monthly）
    
    # 关联信息
    source_message_id = Column(Integer)  # 创建来源的消息ID
    
    # 完成信息
    completed_at = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, title={self.title}, time={self.schedule_time})>"


class ScheduleReminder(Base):
    """日程提醒记录表"""
    __tablename__ = "schedule_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 提醒信息
    reminded_at = Column(DateTime, default=datetime.utcnow)
    reminder_message = Column(Text)
    
    # 用户响应
    user_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ScheduleReminder(schedule_id={self.schedule_id}, reminded_at={self.reminded_at})>"
