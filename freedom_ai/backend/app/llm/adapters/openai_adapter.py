"""
OpenAI API适配器
支持OpenAI和兼容OpenAI格式的API
"""
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI
from app.llm.adapters.base import BaseLLMAdapter
from app.core.logging import app_logger


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI适配器"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, base_url, model)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """发送聊天请求"""
        try:
            formatted_messages = self.format_messages(messages)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            content = response.choices[0].message.content
            app_logger.debug(f"OpenAI响应: {content[:100]}...")
            return content
            
        except Exception as e:
            app_logger.error(f"OpenAI API调用失败: {str(e)}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """流式聊天请求"""
        try:
            formatted_messages = self.format_messages(messages)
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            app_logger.error(f"OpenAI流式调用失败: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """计算token数量（简单估算）"""
        # 简单估算：中文约1.5字符/token，英文约4字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """格式化消息为OpenAI格式"""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return formatted
