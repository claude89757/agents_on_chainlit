"""
创建Autogen团队实例
"""

import os

import chainlit as cl
from chainlit import logger

# autogen_agentchat相关导入
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, ExternalTermination
from autogen_agentchat.teams import RoundRobinGroupChat

# autogen_ext相关导入
from autogen_ext.tools.mcp import StdioServerParams
from autogen_ext.tools.mcp import McpWorkbench

# llm相关导入
from llm.openrouter import get_model_client


async def setup_autogen_team():
    """
    初始化模型客户端和代理团队
    返回：
    - team: 团队实例
    - external_termination: 外部终止条件实例
    - mcp_workbench: MCP工作台实例
    """
    # 初始化模型
    logger.info("初始化模型...")
    model_name = cl.user_session.get("chat_settings").get("model")
    model_client = get_model_client(model_name)

    # 初始化MCP
    logger.info("初始化MCP...")
    mcp_server_params = StdioServerParams(
        command="npx",
        args=[
            "@playwright/mcp@latest",
            "--headless"
        ],
        env={},
        read_timeout_seconds=60.0,
    )
    mcp_workbench = McpWorkbench(mcp_server_params)
    await mcp_workbench.start()
 
    # 初始化Agent
    logger.info("初始化Agent...")
    executor_agent = AssistantAgent(
        name="Executor",
        model_client=model_client,
        reflect_on_tool_use=False,
        model_client_stream=True,
        workbench=mcp_workbench,
        description="A expert of using API",
        system_message="""<role>
        你是小红书资源操作专家，负责使用MCP工具执行小红书资源的各项操作。你擅长调用小红书API来完成资源的查询、创建、删除等动作。
        </role>

        <knowledge>
        </knowledge>

        <instruction>
        - 先根据用户任务<task>和业务知识<knowledge>，进行任务规划, 并且会在过程中动态调整任务规划
        - 完成任务规划后，再使用mcp工具调用小红书API，执行具体的资源操作任务
        - 执行后提供简洁清晰的结果摘要，包括：
        * 操作是否成功
        * 返回的关键信息（如资源ID、状态等）
        * 下一步的行动计划
        - 最后记住，如果全部任务完成，在回复的最后添加"TERMINATE"标记
        </instruction>""")
    
    # 设置团队
    logger.info("设置团队...")
    external_termination = ExternalTermination()
    termination_condition = TextMentionTermination("TERMINATE") | external_termination
    team = RoundRobinGroupChat(
        participants=[executor_agent],
        termination_condition= termination_condition,
        max_turns=10,
        emit_team_events=True
    )

    logger.info("团队创建完成，准备开始工作")
    return team, external_termination, mcp_workbench
    

async def dissmiss_autogen_team(team, external_termination, mcp_workbench):
    """
    解散Autogen团队
    """
    # 解散Autogen团队实例
    try:
        if team:
            logger.info("暂停Autogen团队...")
            await team.pause()
            logger.info("保存Autogen团队状态...")
            team_state = await team.save_state()

            # TODO: team_state要持久化，下次启动时恢复
            logger.info("*"*100)
            logger.info(f"[INFO] Team State: {team_state}")
            logger.info("*"*100)
    except Exception as error:
        logger.error(f"[ERROR] Error ending autogen team: {error}")

    try:
        if mcp_workbench:
            logger.info("暂停MCP工作台...")
            await mcp_workbench.stop()
            logger.info("MCP工作台已停止")
    except Exception as error:
        logger.error(f"[ERROR] Error stopping mcp workbench: {error}")
        
    try:
        if external_termination:
            logger.info("终止Autogen团队...")
            await external_termination.set()
            logger.info("Autogen团队已终止")
    except Exception as error:
        logger.error(f"[ERROR] Error stopping external termination: {error}")
