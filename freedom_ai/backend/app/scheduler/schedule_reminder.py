"""
日程提醒调度器
定时检查并发送日程提醒
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.logging import app_logger
from app.db.database import SessionLocal
from app.services.schedule_service import ScheduleService
from app.models.schedule import ScheduleReminder


reminder_scheduler = BackgroundScheduler()


def check_and_send_reminders():
    """检查并发送日程提醒"""
    db = SessionLocal()
    try:
        schedule_service = ScheduleService(db)
        
        # 获取需要提醒的日程
        pending_schedules = schedule_service.get_pending_reminders()
        
        for schedule in pending_schedules:
            # 生成提醒消息
            reminder_message = f"⏰ 提醒：{schedule.title}\n"
            if schedule.description:
                reminder_message += f"详情：{schedule.description}\n"
            reminder_message += f"时间：{schedule.schedule_time.strftime('%Y-%m-%d %H:%M')}"
            
            # 记录提醒
            reminder = ScheduleReminder(
                schedule_id=schedule.id,
                user_id=schedule.user_id,
                reminder_message=reminder_message
            )
            db.add(reminder)
            
            # 标记为已提醒
            schedule_service.mark_as_reminded(schedule.id)
            
            # 通过WebSocket发送提醒（如果用户在线）
            try:
                from app.api.v1.endpoints.websocket import send_proactive_message
                from app.models.user import User
                
                user = db.query(User).filter(User.id == schedule.user_id).first()
                if user and user.is_online:
                    import asyncio
                    asyncio.run(send_proactive_message(user.username, reminder_message))
                    app_logger.info(f"发送日程提醒: {schedule.title} -> {user.username}")
            except Exception as e:
                app_logger.error(f"发送日程提醒失败: {str(e)}")
        
        db.commit()
        
        if pending_schedules:
            app_logger.info(f"处理了 {len(pending_schedules)} 个日程提醒")
        
    except Exception as e:
        app_logger.error(f"日程提醒调度失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def start_schedule_reminder():
    """启动日程提醒调度器"""
    # 每分钟检查一次
    reminder_scheduler.add_job(
        check_and_send_reminders,
        'interval',
        minutes=1,
        id='schedule_reminder',
        replace_existing=True
    )
    
    reminder_scheduler.start()
    app_logger.info("日程提醒调度器已启动，间隔: 1分钟")


def stop_schedule_reminder():
    """停止日程提醒调度器"""
    if reminder_scheduler.running:
        reminder_scheduler.shutdown()
        app_logger.info("日程提醒调度器已停止")
