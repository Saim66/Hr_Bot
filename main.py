import os
import logging
from highrise import BaseBot
from commands import CommandHandler

logging.basicConfig(level=logging.INFO)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata):
        logging.info(f"✅ Bot Online in: {session_metadata.room_info.room_name}")

    async def on_chat(self, user, message):
        await self.cmd.execute(user, message)

    async def on_user_join(self, user):
        # We keep this silent to avoid API triggers that cause disconnects
        logging.info(f"User {user.username} joined.")