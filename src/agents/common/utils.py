from chainlit import logger


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
