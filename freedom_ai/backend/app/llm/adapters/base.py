"""
LLM适配器基类
定义统一的LLM接口规范
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator


class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            AI的回复内容
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            逐个生成的token
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            token数量
        """
        pass
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        格式化消息（可被子类覆盖）
        
        Args:
            messages: 原始消息列表
            
        Returns:
            格式化后的消息列表
        """
        return messages
    
    async def validate_connection(self) -> bool:
        """
        验证连接是否正常
        
        Returns:
            连接是否成功
        """
        try:
            test_messages = [{"role": "user", "content": "Hi"}]
            response = await self.chat(test_messages, max_tokens=10)
            return bool(response)
        except Exception:
            return False
