"""
记忆管理器
管理短期记忆和长期记忆
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.message import Message, MessageRole
from app.memory.vector_store import get_vector_store
from app.core.config import settings
from app.core.logging import app_logger


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store()
    
    async def add_conversation_to_memory(
        self,
        user_id: int,
        messages: List[Message],
        importance: float = 0.5
    ) -> List[str]:
        """
        将对话添加到长期记忆
        
        Args:
            user_id: 用户ID
            messages: 消息列表
            importance: 重要性评分
            
        Returns:
            添加的记忆ID列表
        """
        memory_ids = []
        
        for msg in messages:
            # 只保存用户消息到长期记忆
            if msg.role == MessageRole.USER and len(msg.content) > 10:
                memory_id = await self.create_memory(
                    user_id=user_id,
                    content=msg.content,
                    category="conversation",
                    importance=importance,
                    source_message_id=msg.id
                )
                if memory_id:
                    memory_ids.append(memory_id)
        
        return memory_ids
    
    async def create_memory(
        self,
        user_id: int,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        source_message_id: Optional[int] = None,
        keywords: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        创建新记忆
        
        Args:
            user_id: 用户ID
            content: 记忆内容
            category: 记忆分类
            importance: 重要性（0-1）
            source_message_id: 来源消息ID
            keywords: 关键词列表
            
        Returns:
            记忆ID
        """
        try:
            # 添加到向量数据库
            metadata = {
                "user_id": user_id,
                "category": category,
                "importance": importance,
                "created_at": datetime.utcnow().isoformat()
            }
            
            vector_id = self.vector_store.add_memory(
                content=content,
                metadata=metadata
            )
            
            # 添加到关系数据库
            memory = Memory(
                user_id=user_id,
                content=content,
                category=category,
                importance=importance,
                vector_id=vector_id,
                source_message_ids=str(source_message_id) if source_message_id else "",
                related_keywords=",".join(keywords) if keywords else ""
            )
            
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
            app_logger.info(f"创建记忆成功: user_id={user_id}, category={category}")
            return vector_id
            
        except Exception as e:
            app_logger.error(f"创建记忆失败: {str(e)}")
            self.db.rollback()
            return None
    
    async def retrieve_relevant_memories(
        self,
        user_id: int,
        query: str,
        n_results: int = None,
        category: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        检索相关记忆
        
        Args:
            user_id: 用户ID
            query: 查询内容
            n_results: 返回数量
            category: 分类过滤
            min_importance: 最小重要性阈值
            
        Returns:
            相关记忆列表
        """
        if n_results is None:
            n_results = settings.long_term_memory_retrieve_size
        
        # 从向量数据库检索
        memories = self.vector_store.search_memories(
            query=query,
            user_id=user_id,
            n_results=n_results * 2,  # 获取更多结果用于过滤
            category=category
        )
        
        # 过滤和排序
        filtered_memories = []
        for mem in memories:
            if mem['metadata'].get('importance', 0) >= min_importance:
                filtered_memories.append(mem)
                
                # 更新访问计数
                self._update_memory_access(mem['id'])
        
        # 返回指定数量
        return filtered_memories[:n_results]
    
    def get_short_term_memory(
        self,
        user_id: int,
        limit: int = None
    ) -> List[Dict]:
        """
        获取短期记忆（最近的对话）
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            
        Returns:
            最近的消息列表
        """
        if limit is None:
            limit = settings.short_term_memory_size
        
        messages = self.db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(
            Message.created_at.desc()
        ).limit(limit).all()
        
        # 反转顺序，使其按时间正序
        messages.reverse()
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def _update_memory_access(self, vector_id: str):
        """更新记忆访问记录"""
        try:
            memory = self.db.query(Memory).filter(
                Memory.vector_id == vector_id
            ).first()
            
            if memory:
                memory.access_count += 1
                memory.last_accessed_at = datetime.utcnow()
                self.db.commit()
        except Exception as e:
            app_logger.error(f"更新记忆访问失败: {str(e)}")
            self.db.rollback()
    
    async def summarize_and_store(
        self,
        user_id: int,
        conversation: str,
        llm_adapter
    ) -> Optional[str]:
        """
        使用LLM总结对话并存储为记忆
        
        Args:
            user_id: 用户ID
            conversation: 对话内容
            llm_adapter: LLM适配器
            
        Returns:
            记忆ID
        """
        from app.core.prompts import prompts
        
        try:
            # 使用LLM提取关键信息
            summary_prompt = prompts.get_memory_summary_prompt(conversation)
            summary = await llm_adapter.chat(
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=500
            )
            
            if summary and len(summary.strip()) > 5:
                # 存储总结
                memory_id = await self.create_memory(
                    user_id=user_id,
                    content=summary,
                    category="summary",
                    importance=0.7
                )
                return memory_id
            
        except Exception as e:
            app_logger.error(f"总结对话失败: {str(e)}")
        
        return None
    
    def get_user_profile_summary(self, user_id: int) -> Dict:
        """
        获取用户画像摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像字典
        """
        # 获取用户的个人信息类记忆
        personal_memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.category == "personal_info",
            Memory.is_active == True
        ).all()
        
        profile = {
            "interests": [],
            "preferences": [],
            "important_dates": [],
            "habits": []
        }
        
        for mem in personal_memories:
            # 简单分类（实际应用中可以使用更智能的方法）
            content = mem.content.lower()
            if "喜欢" in content or "兴趣" in content:
                profile["interests"].append(mem.content)
            elif "偏好" in content or "习惯" in content:
                profile["habits"].append(mem.content)
        
        return profile


def get_memory_manager(db: Session) -> MemoryManager:
    """获取记忆管理器实例"""
    return MemoryManager(db)
