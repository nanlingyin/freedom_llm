"""
Claude (Anthropic) API适配器
"""
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from app.llm.adapters.base import BaseLLMAdapter
from app.core.logging import app_logger


class ClaudeAdapter(BaseLLMAdapter):
    """Claude适配器"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, base_url, model)
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """发送聊天请求"""
        try:
            # Claude需要分离system消息
            system_msg, formatted_messages = self._extract_system_message(messages)
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg if system_msg else None,
                messages=formatted_messages
            )
            
            content = response.content[0].text
            app_logger.debug(f"Claude响应: {content[:100]}...")
            return content
            
        except Exception as e:
            app_logger.error(f"Claude API调用失败: {str(e)}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """流式聊天请求"""
        try:
            system_msg, formatted_messages = self._extract_system_message(messages)
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg if system_msg else None,
                messages=formatted_messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            app_logger.error(f"Claude流式调用失败: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """计算token数量（简单估算）"""
        # 使用与OpenAI相同的估算方法
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)
    
    def _extract_system_message(self, messages: List[Dict[str, str]]) -> tuple[str, List[Dict[str, str]]]:
        """
        提取system消息和格式化其他消息
        Claude的API要求system消息单独传递
        """
        system_msg = ""
        formatted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return system_msg, formatted_messages
