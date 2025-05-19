"""
应用入口点模块

包含Chainlit应用的主要逻辑，如会话启动和消息处理
"""

# 第三方库导入
import chainlit as cl
from chainlit import logger
from chainlit.input_widget import Select, Slider, Switch, Tags, TextInput, NumberInput


# 支持的模型列表
SUPPORTED_MODELS = [
    "anthropic/claude-3.7-sonnet"
]


# --- Chainlit应用逻辑 ---
async def on_chat_start():
    """
    初始化Chainlit的聊天会话, 可以加载配置文件、初始化模型、初始化团队等
    """
    # 设置chat_settings
    await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Models from Venus",
                values=SUPPORTED_MODELS,
                initial_index=0,
            )
        ]
    ).send()

    logger.info(f"[INFO] Chat Settings: {cl.user_session.get('chat_settings')}")

    # # 用于UI上显示模型的使用情况
    # cl.instrument_openai()


async def on_message(message: cl.Message):
    """
    处理用户的消息
    """
    logger.info(f"[INFO] On Message: {message}")
    pass
