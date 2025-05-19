
import os
import sys
from typing import cast

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chainlit as cl
from chainlit import logger
from typing import Any
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.messages import ModelClientStreamingChunkEvent
from autogen_agentchat.base import TaskResult
from autogen_core import CancellationToken


async def autogen_team_output(autogen_team: Any, message_content: str):
    # Streaming response message.
    streaming_response: cl.Message | None = None
    try:
        task = [TextMessage(content=message_content, source="user_input")]
        async for msg in autogen_team.run_stream(task=task, cancellation_token=CancellationToken()):  
            if isinstance(msg, ModelClientStreamingChunkEvent):
                # Stream the model client response to the user.
                if streaming_response is None:
                    # Start a new streaming response.
                    streaming_response = cl.Message(content=msg.source + ": ", author=msg.source)
                await streaming_response.stream_token(msg.content)
            elif streaming_response is not None:
                # Done streaming the model client response.
                # We can skip the current message as it is just the complete message
                # of the streaming response.
                await streaming_response.send()
                # Reset the streaming response so we won't enter this block again
                # until the next streaming response is complete.
                streaming_response = None
            elif isinstance(msg, TaskResult):
                # Send the task termination message.
                await cl.Message(content=f"Stop Reason: {msg.stop_reason}", author="PcapAgent").send()
            else:
                # 使用Step类处理其他消息类型
                message_content = str(msg.content) if hasattr(msg, "content") else ""
                message_type = msg.type if hasattr(msg, "type") else "unknown"
                message_source = msg.source if hasattr(msg, "source") else "unknown"
                message_models_usage = msg.models_usage if hasattr(msg, "models_usage") else None
                
                # 确保内容不为空
                if not message_content:
                    message_content = "空内容"
                
                # 使用固定的Chainlit支持的类型"tool"
                async with cl.Step(name=f"{message_source} {message_type}", type="tool") as step:
                    # 设置输入和输出
                    step.input = message_content  # 用户的查询
                    step.output = message_content  # 代理的输出
                    
                    # 添加文本元素
                    text_element = cl.Text(
                        name=message_type, 
                        content=message_content,
                        display="inline",
                        language="text"
                    )
                    
                    # 将元素添加到步骤中
                    step.elements = [text_element]
                    
                    # 添加模型使用信息
                    if message_models_usage:
                        usage_text = cl.Text(
                            name="模型使用情况",
                            content=f"消耗: {message_models_usage}",
                            language="text"
                        )
                        step.elements.append(usage_text)
           
    except Exception as error:
        import traceback
        error_detail = f"autogen_team_output 发生错误: {traceback.format_exc()}"
        logger.error(f"[ERROR] {error_detail}\n{traceback.format_exc()} {error}")
        await cl.Message(content=error_detail, author="系统错误").send() 
