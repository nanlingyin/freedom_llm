"""
主动对话调度器
定时触发AI主动发起对话
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import random
from app.core.config import settings
from app.core.logging import app_logger
from app.core.prompts import prompts
from app.db.database import SessionLocal
from app.models.user import User
from app.models.message import Message, MessageRole
from app.llm.factory import get_global_llm
from app.memory.memory_manager import MemoryManager


scheduler = BackgroundScheduler()


async def generate_proactive_message(user_id: int) -> str:
    """
    生成主动对话消息
    
    Args:
        user_id: 用户ID
        
    Returns:
        生成的消息内容
    """
    db = SessionLocal()
    try:
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return ""
        
        # 获取最近话题
        recent_messages = db.query(Message).filter(
            Message.user_id == user_id,
            Message.role == MessageRole.USER
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        recent_topics = [msg.content[:50] for msg in recent_messages]
        
        # 获取用户画像
        memory_manager = MemoryManager(db)
        user_profile = memory_manager.get_user_profile_summary(user_id)
        
        # 构建提示词
        user_info_str = f"""
        用户名: {user.username}
        昵称: {user.nickname or user.username}
        画像: {user_profile}
        """
        
        prompt = prompts.get_proactive_chat_prompt(
            user_info=user_info_str,
            recent_topics=recent_topics
        )
        
        # 调用LLM生成消息
        llm = get_global_llm()
        message = await llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )
        
        # 保存主动消息
        proactive_msg = Message(
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=message,
            is_proactive=True
        )
        db.add(proactive_msg)
        db.commit()
        
        app_logger.info(f"生成主动消息: user_id={user_id}, content={message[:50]}...")
        return message
        
    except Exception as e:
        app_logger.error(f"生成主动消息失败: {str(e)}")
        return ""
    finally:
        db.close()


def check_and_send_proactive_messages():
    """检查并发送主动消息"""
    if not settings.proactive_chat_enabled:
        return
    
    db = SessionLocal()
    try:
        # 获取在线且活跃的用户
        current_hour = datetime.utcnow().hour
        
        # 检查当前时间是否在用户活跃时间段
        if current_hour not in settings.user_active_hours:
            return
        
        # 获取所有活跃用户
        users = db.query(User).filter(
            User.is_active == True,
            User.is_online == True
        ).all()
        
        for user in users:
            # 检查上次主动消息时间
            last_proactive = db.query(Message).filter(
                Message.user_id == user.id,
                Message.is_proactive == True
            ).order_by(Message.created_at.desc()).first()
            
            # 如果最近没有主动消息，或者距离上次已经足够久
            should_send = False
            if not last_proactive:
                should_send = True
            else:
                time_since_last = (datetime.utcnow() - last_proactive.created_at).total_seconds()
                min_interval = settings.proactive_chat_min_interval
                if time_since_last > min_interval:
                    # 随机决定是否发送（增加自然性）
                    should_send = random.random() > 0.5
            
            if should_send:
                # 异步生成并发送消息
                import asyncio
                message = asyncio.run(generate_proactive_message(user.id))
                
                if message:
                    # 通过WebSocket发送（如果用户在线）
                    from app.api.v1.endpoints.websocket import send_proactive_message
                    asyncio.run(send_proactive_message(user.username, message))
                    app_logger.info(f"发送主动消息给用户: {user.username}")
        
    except Exception as e:
        app_logger.error(f"主动对话调度失败: {str(e)}")
    finally:
        db.close()


def start_proactive_chat_scheduler():
    """启动主动对话调度器"""
    if not settings.proactive_chat_enabled:
        app_logger.info("主动对话功能已禁用")
        return
    
    # 每30分钟检查一次
    scheduler.add_job(
        check_and_send_proactive_messages,
        'interval',
        minutes=30,
        id='proactive_chat',
        replace_existing=True
    )
    
    scheduler.start()
    app_logger.info("主动对话调度器已启动，间隔: 30分钟")


def stop_proactive_chat_scheduler():
    """停止主动对话调度器"""
    if scheduler.running:
        scheduler.shutdown()
        app_logger.info("主动对话调度器已停止")
