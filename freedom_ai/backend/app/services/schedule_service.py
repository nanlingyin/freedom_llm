"""
日程服务层
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.schedule import Schedule, ScheduleStatus, SchedulePriority
from app.core.config import settings
from app.core.logging import app_logger


class ScheduleService:
    """日程服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_schedule(
        self,
        user_id: int,
        title: str,
        schedule_time: str,
        description: Optional[str] = None,
        priority: str = "medium",
        source_message_id: Optional[int] = None
    ) -> Schedule:
        """
        创建日程
        
        Args:
            user_id: 用户ID
            title: 日程标题
            schedule_time: 日程时间（ISO格式字符串）
            description: 描述
            priority: 优先级
            source_message_id: 来源消息ID
            
        Returns:
            创建的日程对象
        """
        # 解析时间
        schedule_dt = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
        
        # 计算提醒时间
        remind_at = schedule_dt - timedelta(minutes=settings.schedule_remind_advance_minutes)
        
        schedule = Schedule(
            user_id=user_id,
            title=title,
            description=description,
            schedule_time=schedule_dt,
            remind_at=remind_at,
            remind_advance_minutes=settings.schedule_remind_advance_minutes,
            priority=SchedulePriority(priority),
            source_message_id=source_message_id
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        app_logger.info(f"创建日程: {title}, 时间: {schedule_time}")
        return schedule
    
    def get_user_schedules(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Schedule]:
        """
        获取用户的日程列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            limit: 返回数量
            
        Returns:
            日程列表
        """
        query = self.db.query(Schedule).filter(Schedule.user_id == user_id)
        
        if status:
            query = query.filter(Schedule.status == ScheduleStatus(status))
        
        schedules = query.order_by(Schedule.schedule_time).limit(limit).all()
        return schedules
    
    def get_pending_reminders(self) -> List[Schedule]:
        """获取需要提醒的日程"""
        now = datetime.utcnow()
        
        schedules = self.db.query(Schedule).filter(
            Schedule.status == ScheduleStatus.PENDING,
            Schedule.remind_at <= now,
            Schedule.schedule_time > now
        ).all()
        
        return schedules
    
    def mark_as_reminded(self, schedule_id: int):
        """标记日程为已提醒"""
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.status = ScheduleStatus.REMINDED
            self.db.commit()
            app_logger.debug(f"标记日程为已提醒: {schedule_id}")
    
    def complete_schedule(self, schedule_id: int):
        """完成日程"""
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.status = ScheduleStatus.COMPLETED
            schedule.completed_at = datetime.utcnow()
            self.db.commit()
            app_logger.info(f"完成日程: {schedule_id}")
    
    def delete_schedule(self, schedule_id: int):
        """删除日程"""
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            self.db.delete(schedule)
            self.db.commit()
            app_logger.info(f"删除日程: {schedule_id}")


def get_schedule_service(db: Session) -> ScheduleService:
    """获取日程服务实例"""
    return ScheduleService(db)
