#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetGen应用程序入口文件
提供Chainlit应用程序的配置和初始化
"""

import chainlit as cl
from chainlit import logger
from typing import Dict

# 登录认证
from auth.password_auth import auth_callback

# 聊天配置
from chat_profiles.profiles import chat_profiles

# 导入各个agent的初始化函数
# tencentcloudagent
from agents.xhsagent.app import on_chat_start as xhsagent_on_chat_start
from agents.xhsagent.team import setup_autogen_team as xhsagent_setup_autogen_team

from agents.common.utils import dissmiss_autogen_team

from chat_output.autogen_team import autogen_team_output


@cl.on_chat_start
async def on_chat_start():
    """
    当用户开始聊天时，会调用这个函数。这里建议初始化agent团队，mcp等。
    """
    user = cl.user_session.get("user")
    logger.info(f"[INFO] On Chat Start with user: {user} with chat_profile: {cl.user_session.get('chat_profile')}")
    agent_name = cl.user_session.get("chat_profile").lower()

    try:
        # 自定义的聊天配置
        func_name = f"{agent_name}_on_chat_start"
        if func_name in globals():
            logger.info(f"[INFO] 找到{agent_name}的独立初始化聊天函数，调用独立初始化聊天函数")
            await globals()[func_name]()
        else:
            logger.info(f"[INFO] 未找到{agent_name}的独立初始化聊天函数，使用默认初始化聊天函数")
            pass

        # 通用的Autogen团队初始化
        logger.info("="*100)
        logger.info("初始化Autogen团队...")
        setup_autogen_team = globals()[f"{agent_name}_setup_autogen_team"]
        autogen_team, external_termination, mcp_workbench = await setup_autogen_team()
        cl.user_session.set("autogen_team", autogen_team)
        cl.user_session.set("autogen_team_external_termination", external_termination)
        cl.user_session.set("autogen_team_mcp_workbench", mcp_workbench)
        logger.info("初始化Autogen团队完成")
        logger.info("="*100)

    except Exception as error:
        import traceback
        error_detail = f"初始化Autogen团队时发生错误: {traceback.format_exc()}"
        logger.error(f"[ERROR] {error_detail}\n{traceback.format_exc()} {error}")
        await cl.Message(content=error_detail, author="系统错误").send() 
    

@cl.on_message
async def on_message(message: cl.Message):
    """
    当用户发送消息时，会调用这个函数。
    """
    logger.info(f"[INFO] On Message: {message}")
    
    # 根据当前会话的chat_profile调用对应的处理函数
    agent_name = cl.user_session.get("chat_profile").lower()
    on_message_func_name = f"{agent_name}_on_message"
    setup_autogen_team = globals()[f"{agent_name}_setup_autogen_team"]
    if on_message_func_name in globals():
        # 自定义的消息处理
        logger.info(f"[INFO] 找到{agent_name}的独立处理消息函数，调用独立处理消息函数")
        await globals()[on_message_func_name](message)
    else:
        # 通用的消息处理
        logger.info(f"[INFO] 未找到{agent_name}的独立处理消息函数，使用默认处理消息函数")
        try:
            # 初始化Autogen的团队实例
            autogen_team = cl.user_session.get("autogen_team")
            if autogen_team is None:
                autogen_team, external_termination, mcp_workbench = await setup_autogen_team()
                cl.user_session.set("autogen_team", autogen_team)
                cl.user_session.set("autogen_team_external_termination", external_termination)
                cl.user_session.set("autogen_team_mcp_workbench", mcp_workbench)
                logger.info("[INFO] Autogen team initialized.")
            else:
                logger.info("[INFO] Autogen team already initialized.")
            
            # 重新格式化用户输入（建议这样做，避免用户输入的格式影响agent的执行）
            reformed_message_content = f"""<task>{message.content}</task>"""

            # 使用Autogen团队运行任务
            await autogen_team_output(autogen_team, reformed_message_content)

        except Exception as error:
            import traceback
            error_detail = f"调用Autogen团队时发生错误: {traceback.format_exc()}"
            logger.error(f"[ERROR] {error_detail}\n{traceback.format_exc()} {error}")
            await cl.Message(content=error_detail, author="系统错误").send() 


@cl.on_chat_end
async def on_chat_end():
    """
    当用户结束聊天时，会调用这个函数。
    """
    logger.info("Chat ended")
    autogen_team = cl.user_session.get("autogen_team")
    external_termination = cl.user_session.get("autogen_team_external_termination")
    mcp_workbench = cl.user_session.get("autogen_team_mcp_workbench")
    
    # 解散Autogen团队实例
    await dissmiss_autogen_team(autogen_team, external_termination, mcp_workbench)

@cl.on_stop
async def on_stop():
    """
    当用户停止聊天时，会调用这个函数。
    """
    logger.info("Chat stopped")
    autogen_team = cl.user_session.get("autogen_team")
    external_termination = cl.user_session.get("autogen_team_external_termination")
    mcp_workbench = cl.user_session.get("autogen_team_mcp_workbench")
    
    # 解散Autogen团队实例
    await dissmiss_autogen_team(autogen_team, external_termination, mcp_workbench)

@cl.on_chat_resume
async def on_chat_resume():
    """
    当用户恢复聊天时，会调用这个函数。
    """
    logger.info(f"Chat Resume")
    # TODO: 还原Autogen团队实例


@cl.on_settings_update
async def on_settings_update(settings: Dict):
    """
    当用户更新设置时，会调用这个函数。
    """
    logger.info(f"Settings updated: {settings}")
    
    # 通用的Autogen团队初始化
    agent_name = cl.user_session.get("chat_profile").lower()
    logger.info("="*100)
    logger.info("初始化Autogen团队...")
    setup_autogen_team = globals()[f"{agent_name}_setup_autogen_team"]
    autogen_team, external_termination, mcp_workbench = await setup_autogen_team()
    cl.user_session.set("autogen_team", autogen_team)
    cl.user_session.set("autogen_team_external_termination", external_termination)
    cl.user_session.set("autogen_team_mcp_workbench", mcp_workbench)
    logger.info("初始化Autogen团队完成")
    logger.info("="*100)
