import os
import chainlit as cl
from chainlit import logger

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # and compare the hashed password with the value stored in the database
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if (username, password) == (username, password):
        logger.info(f"[INFO] Auth Success: {username}")
        return cl.User(
            identifier=username, metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        logger.info(f"[INFO] Auth Failed: {username}")
        return None

@cl.on_logout
async def on_logout():
    logger.info(f"[INFO] On Logout")
    return None
