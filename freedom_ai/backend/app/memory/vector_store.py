"""
向量存储模块
使用ChromaDB进行向量化记忆存储和检索
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import app_logger
import uuid


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self):
        """初始化向量数据库"""
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "用户记忆存储"}
        )
        app_logger.info(f"向量数据库初始化完成，路径: {settings.vector_db_path}")
    
    def add_memory(
        self,
        content: str,
        metadata: Dict,
        memory_id: Optional[str] = None
    ) -> str:
        """
        添加记忆到向量数据库
        
        Args:
            content: 记忆内容
            metadata: 元数据（用户ID、分类、时间戳等）
            memory_id: 记忆ID（可选，如果不提供则自动生成）
            
        Returns:
            记忆ID
        """
        if memory_id is None:
            memory_id = str(uuid.uuid4())
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
            app_logger.debug(f"添加记忆成功: {memory_id}, 内容: {content[:50]}...")
            return memory_id
        except Exception as e:
            app_logger.error(f"添加记忆失败: {str(e)}")
            raise
    
    def search_memories(
        self,
        query: str,
        user_id: int,
        n_results: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索相关记忆
        
        Args:
            query: 查询文本
            user_id: 用户ID
            n_results: 返回结果数量
            category: 记忆分类过滤
            
        Returns:
            相关记忆列表
        """
        try:
            # 构建where条件
            where_filter = {"user_id": user_id}
            if category:
                where_filter["category"] = category
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # 格式化结果
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        "id": results['ids'][0][i],
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            app_logger.debug(f"检索到 {len(memories)} 条相关记忆")
            return memories
            
        except Exception as e:
            app_logger.error(f"搜索记忆失败: {str(e)}")
            return []
    
    def update_memory(self, memory_id: str, content: str, metadata: Dict):
        """
        更新记忆
        
        Args:
            memory_id: 记忆ID
            content: 新内容
            metadata: 新元数据
        """
        try:
            self.collection.update(
                ids=[memory_id],
                documents=[content],
                metadatas=[metadata]
            )
            app_logger.debug(f"更新记忆成功: {memory_id}")
        except Exception as e:
            app_logger.error(f"更新记忆失败: {str(e)}")
            raise
    
    def delete_memory(self, memory_id: str):
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
        """
        try:
            self.collection.delete(ids=[memory_id])
            app_logger.debug(f"删除记忆成功: {memory_id}")
        except Exception as e:
            app_logger.error(f"删除记忆失败: {str(e)}")
            raise
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Dict]:
        """
        根据ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆内容
        """
        try:
            result = self.collection.get(ids=[memory_id])
            if result['documents']:
                return {
                    "id": result['ids'][0],
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0]
                }
            return None
        except Exception as e:
            app_logger.error(f"获取记忆失败: {str(e)}")
            return None
    
    def clear_user_memories(self, user_id: int):
        """
        清除用户的所有记忆
        
        Args:
            user_id: 用户ID
        """
        try:
            # 获取该用户的所有记忆ID
            results = self.collection.get(where={"user_id": user_id})
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                app_logger.info(f"清除用户 {user_id} 的所有记忆，共 {len(results['ids'])} 条")
        except Exception as e:
            app_logger.error(f"清除用户记忆失败: {str(e)}")
            raise


# 创建全局向量存储实例
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """获取全局向量存储实例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
