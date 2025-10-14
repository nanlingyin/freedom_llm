"""
LLM适配器工厂
根据配置创建相应的LLM适配器实例
"""
from typing import Optional
from app.llm.adapters.base import BaseLLMAdapter
from app.llm.adapters.openai_adapter import OpenAIAdapter
from app.llm.adapters.claude_adapter import ClaudeAdapter
from app.core.config import settings
from app.core.logging import app_logger


class LLMFactory:
    """LLM工厂类"""
    
    _adapters = {
        "openai": OpenAIAdapter,
        "claude": ClaudeAdapter,
        "anthropic": ClaudeAdapter,
        # 可以继续添加其他适配器
        "gemini": OpenAIAdapter,  # 如果使用兼容OpenAI格式的代理
        "qwen": OpenAIAdapter,    # 通义千问兼容OpenAI格式
        "zhipu": OpenAIAdapter,   # 智谱AI兼容OpenAI格式
        "deepseek": OpenAIAdapter, # DeepSeek兼容OpenAI格式
    }
    
    @classmethod
    def create_adapter(
        cls,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMAdapter:
        """
        创建LLM适配器实例
        
        Args:
            provider: LLM提供商名称
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            
        Returns:
            LLM适配器实例
        """
        # 使用配置文件中的默认值
        provider = provider or settings.llm_provider
        api_key = api_key or settings.llm_api_key
        base_url = base_url or settings.llm_base_url
        model = model or settings.llm_model
        
        # 验证API密钥
        if not api_key:
            raise ValueError("API密钥不能为空，请在.env文件中配置LLM_API_KEY")
        
        # 获取适配器类
        adapter_class = cls._adapters.get(provider.lower())
        if not adapter_class:
            app_logger.warning(f"未知的LLM提供商: {provider}，使用OpenAI适配器")
            adapter_class = OpenAIAdapter
        
        # 创建适配器实例
        app_logger.info(f"创建LLM适配器: provider={provider}, model={model}")
        return adapter_class(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
    
    @classmethod
    def register_adapter(cls, provider: str, adapter_class: type):
        """
        注册新的适配器
        
        Args:
            provider: 提供商名称
            adapter_class: 适配器类
        """
        cls._adapters[provider.lower()] = adapter_class
        app_logger.info(f"注册LLM适配器: {provider}")


# 创建全局LLM适配器实例
def get_llm_adapter() -> BaseLLMAdapter:
    """获取全局LLM适配器实例"""
    return LLMFactory.create_adapter()


# 单例模式：创建全局实例
_global_adapter: Optional[BaseLLMAdapter] = None


def get_global_llm() -> BaseLLMAdapter:
    """获取全局单例LLM适配器"""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = LLMFactory.create_adapter()
    return _global_adapter


def reset_global_llm():
    """重置全局LLM适配器（用于更新配置后）"""
    global _global_adapter
    _global_adapter = None
