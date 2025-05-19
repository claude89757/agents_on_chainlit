import chainlit as cl
from typing import Optional


@cl.set_chat_profiles
async def chat_profiles(current_user: cl.User):
    """
    设置chat profile
    备注: 各个agent的icon图标可从https://icons.woa.com/获取
    """
    if not current_user:
        return None
    
    return [
        cl.ChatProfile(
            name="xhsagent",
            markdown_description="小红书智能体",
            icon="🤖",
            starters=[
                cl.Starter(
                    label="查询主机列表",
                    message="查询主机列表",
                    # icon="💻",
                ),
                cl.Starter(
                    label="查询手机列表",
                    message="查询手机列表",
                    # icon="📱",
                )
            ],
        ),
    ] 
