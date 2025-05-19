import os
import asyncio
from typing import Union, Dict, Optional

import chainlit as cl
from chainlit import logger

# autogen_agentchat相关导入
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, ExternalTermination
from autogen_agentchat.teams import RoundRobinGroupChat

# autogen_core相关导入
from autogen_core.models import ModelFamily

# autogen_ext相关导入
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams
from autogen_ext.tools.mcp import McpWorkbench

from typing import Optional, Dict

from autogen_core.models import ModelFamily


def get_model_capabilities(model_name: str) -> Optional[Dict]:
    """
    根据模型名称智能推断模型的能力
    
    Args:
        model_name: 模型名称
        
    Returns:
        包含模型能力的字典，如果是标准OpenAI模型则返回None
    """
    model_name_lower = model_name.lower()
    
    # OpenAI系列模型 - 返回None让AutoGen自动处理
    if model_name.startswith("gpt-") :
        return None
    
    # Claude系列模型
    if "claude" in model_name_lower:
        return {
            "vision": True,
            "function_calling": True,  # 新版Claude支持function calling
            "json_output": True,
            "family": ModelFamily.CLAUDE_3_7_SONNET,
            "structured_output": True
        }

    # Qwen系列模型
    if "qwen" in model_name_lower:
        return {
            "vision": "vl" in model_name_lower,  # Qwen-VL支持视觉
            "function_calling": True,  # 大多数Qwen模型支持function calling
            "json_output": True,
            "family": "qwen",
            "structured_output": True
        }
    
    # Gemini系列模型
    if "gemini" in model_name_lower:
        return {
            "vision": True,  # 大多数Gemini模型支持视觉
            "function_calling": True,
            "json_output": True,
            "family": "gemini",
            "structured_output": True
        }
    
    # DeepSeek系列模型
    if "deepseek" in model_name_lower:
        return {
            "vision": "v" in model_name_lower,
            "function_calling": True,
            "json_output": True,
            "family": "deepseek",
            "structured_output": True
        }
    
    raise ValueError(f"未知模型类型: {model_name}")


def get_model_client(model_name: str):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    # 尝试自动检测模型能力
    model_capabilities = get_model_capabilities(model_name)
    
    # 初始化模型客户端
    if model_capabilities:
        logger.info(f"为{model_name}创建模型客户端，能力: {model_capabilities}")
        model_client = OpenAIChatCompletionClient(model=model_name, 
                                                  api_key=api_key, 
                                                  base_url=base_url, 
                                                  model_info=model_capabilities)
    else:
        # 标准OpenAI模型，不需要额外的model_info
        logger.info(f"为标准OpenAI模型{model_name}创建客户端")
        model_client = OpenAIChatCompletionClient(model=model_name, 
                                                  api_key=api_key, 
                                                  base_url=base_url)

    return model_client
