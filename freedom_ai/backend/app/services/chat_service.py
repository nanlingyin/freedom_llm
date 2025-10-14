"""
聊天服务层
处理对话逻辑和记忆管理
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.message import Message, MessageRole, MessageType
from app.models.user import User
from app.memory.memory_manager import MemoryManager
from app.llm.factory import get_global_llm
from app.core.prompts import prompts
from app.core.config import settings
from app.core.logging import app_logger


class ChatService:
    """聊天服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.memory_manager = MemoryManager(db)
        self.llm = get_global_llm()
    
    async def chat(
        self,
        user_id: int,
        user_message: str,
        stream: bool = False
    ) -> Dict:
        """
        处理用户消息并生成回复
        
        Args:
            user_id: 用户ID
            user_message: 用户消息
            stream: 是否流式输出
            
        Returns:
            包含AI回复的字典
        """
        try:
            # 保存用户消息
            user_msg = self._save_message(
                user_id=user_id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # 更新用户活跃状态
            self._update_user_activity(user_id)
            
            # 构建对话上下文
            messages = await self._build_context(user_id, user_message)
            
            # 调用LLM生成回复
            if stream:
                # TODO: 实现流式响应
                ai_response = await self.llm.chat(
                    messages=messages,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
            else:
                ai_response = await self.llm.chat(
                    messages=messages,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
            
            # 保存AI回复
            ai_msg = self._save_message(
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=ai_response
            )
            
            # 异步处理：将重要对话存入长期记忆
            if len(user_message) > 20:
                await self.memory_manager.create_memory(
                    user_id=user_id,
                    content=user_message,
                    category="conversation",
                    importance=0.6
                )
            
            # 检查是否包含日程信息
            await self._check_and_extract_schedule(user_id, user_message, user_msg.id)
            
            return {
                "success": True,
                "message_id": ai_msg.id,
                "content": ai_response,
                "timestamp": ai_msg.created_at.isoformat()
            }
            
        except Exception as e:
            app_logger.error(f"聊天处理失败: {str(e)}")
            return {
                "success": False,
                "error": "处理失败，请稍后重试",
                "detail": str(e)
            }
    
    async def _build_context(self, user_id: int, current_message: str) -> List[Dict]:
        """构建对话上下文"""
        messages = []
        
        # 1. 添加系统提示词
        messages.append({
            "role": "system",
            "content": prompts.get_system_prompt()
        })
        
        # 2. 检索相关的长期记忆
        relevant_memories = await self.memory_manager.retrieve_relevant_memories(
            user_id=user_id,
            query=current_message,
            n_results=3
        )
        
        if relevant_memories:
            memory_context = "相关记忆：\n" + "\n".join(
                [f"- {mem['content']}" for mem in relevant_memories]
            )
            messages.append({
                "role": "system",
                "content": memory_context
            })
        
        # 3. 获取短期记忆（最近对话）
        short_term = self.memory_manager.get_short_term_memory(
            user_id=user_id,
            limit=10
        )
        
        for msg in short_term:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 4. 添加当前用户消息
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def _save_message(
        self,
        user_id: int,
        role: MessageRole,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        is_proactive: bool = False
    ) -> Message:
        """保存消息到数据库"""
        message = Message(
            user_id=user_id,
            role=role,
            content=content,
            message_type=message_type,
            is_proactive=is_proactive,
            token_count=self.llm.count_tokens(content)
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def _update_user_activity(self, user_id: int):
        """更新用户活跃状态"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_active_at = datetime.utcnow()
            user.is_online = True
            
            # 记录活跃时间段
            current_hour = datetime.utcnow().hour
            active_hours = user.active_hours or []
            if current_hour not in active_hours:
                active_hours.append(current_hour)
                user.active_hours = active_hours
            
            self.db.commit()
    
    async def _check_and_extract_schedule(
        self,
        user_id: int,
        message: str,
        message_id: int
    ):
        """检查并提取日程信息"""
        try:
            # 使用LLM提取日程
            extract_prompt = prompts.get_schedule_extract_prompt(message)
            result = await self.llm.chat(
                messages=[{"role": "user", "content": extract_prompt}],
                max_tokens=300
            )
            
            # 解析结果并创建日程
            import json
            schedule_data = json.loads(result)
            
            if schedule_data.get("has_schedule"):
                from app.services.schedule_service import ScheduleService
                schedule_service = ScheduleService(self.db)
                await schedule_service.create_schedule(
                    user_id=user_id,
                    title=schedule_data.get("title", ""),
                    description=schedule_data.get("description", ""),
                    schedule_time=schedule_data.get("datetime"),
                    source_message_id=message_id
                )
                app_logger.info(f"从消息中提取并创建日程: {schedule_data.get('title')}")
                
        except Exception as e:
            app_logger.debug(f"日程提取失败（可能不包含日程信息）: {str(e)}")
    
    async def get_chat_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """获取聊天历史"""
        messages = self.db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(
            Message.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        messages.reverse()
        
        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "is_proactive": msg.is_proactive,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    async def clear_chat_history(self, user_id: int):
        """清除聊天历史"""
        self.db.query(Message).filter(Message.user_id == user_id).delete()
        self.db.commit()
        app_logger.info(f"清除用户 {user_id} 的聊天历史")


def get_chat_service(db: Session) -> ChatService:
    """获取聊天服务实例"""
    return ChatService(db)
