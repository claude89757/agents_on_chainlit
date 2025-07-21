import os
import chainlit as cl
from chainlit import logger

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Validate user credentials against environment variables."""
    env_username = os.getenv("ADMIN_USERNAME")
    env_password = os.getenv("ADMIN_PASSWORD")

    if (username, password) == (env_username, env_password):
        logger.info(f"[INFO] Auth Success: {username}")
        return cl.User(
            identifier=username, metadata={"role": "admin", "provider": "credentials"}
        )

    logger.info(f"[INFO] Auth Failed: {username}")
    return None

@cl.on_logout
async def on_logout():
    logger.info(f"[INFO] On Logout")
    return None
