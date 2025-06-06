"""
Models package - 数据模型模块
包含AI服务提供商、数据结构定义等
"""

from .ai_providers import (
    AIProvider, 
    ZhipuAIProvider, 
    SiliconFlowProvider, 
    AIProviderFactory,
    ZhipuAI,  # 兼容性别名
    DeepSeekAI  # 兼容性别名
)

__all__ = [
    'AIProvider',
    'ZhipuAIProvider',
    'SiliconFlowProvider', 
    'AIProviderFactory',
    'ZhipuAI',
    'DeepSeekAI'
]
