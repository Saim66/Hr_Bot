import os
import asyncio
import logging
from highrise import Position, User, CurrencyItem, Item  #
from highrise import BaseBot, Position, User
from bot_commands import CommandHandler
from typing import Union
from emotes import EMOTE_LIST

# Configure logging for Railway/Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)
        self.data_cache = self.cmd.load_data()
        self._api_lock = asyncio.Semaphore(1) 
        self.dancing_users = set()

    async def on_start(self, session_metadata):
        self.bot_id = session_metadata.user_id
        self.cmd = CommandHandler(self)
        logger.info(f"✅ Bot Online in: {session_metadata.room_info.room_name}")
        asyncio.create_task(self.emote_engine())

    async def safe_api_call(self, coro):
        """Prevents API flooding and handles disconnects silently."""
        async with self._api_lock:
            try:
                return await coro
            except Exception as e:
                logger.warning(f"API call skipped: {e}")
                return None

    async def emote_engine(self):
        while True:
            if hasattr(self.cmd, 'looping_users') and self.cmd.looping_users:
                for user_id, official_id in list(self.cmd.looping_users.items()):
                    await self.safe_api_call(self.highrise.send_emote(official_id, user_id))
                    await asyncio.sleep(2)
            await asyncio.sleep(1)

    async def on_chat(self, user: User, message: str) -> None:
        await self.cmd.execute(user, message)
        # Refresh cache after potential command-based changes
        self.data_cache = self.cmd.load_data()

    # Add 'position' as the third argument
async def on_user_join(self, user: User, position: Position) -> None:
    # Now the signature matches what the SDK expects
    try:
        handler = self.command_handler
        user_lower = user.username.lower()
        
        # 1. Ban/Restricted Check
        if user_lower in handler.data.get("restricted", []):
            await self.highrise.teleport(user.id, Position(0, 0, 0, "FrontLeft"))
            return

        # 2. VIP Check
        if user_lower in handler.data.get("vips", []):
            await self.highrise.chat(f"Welcome back, VIP @{user.username}!")
            return

        # 3. Custom Welcome
        welcomes = handler.data.get("welcomes", {})
        if user_lower in welcomes:
            msg = welcomes[user_lower]
            final_msg = msg.replace("{username}", user.username)
            await self.highrise.chat(f"👋 @{user.username}, {final_msg}")
            
    except Exception as e:
        print(f"Join logic error: {e}")

    async def on_user_leave(self, user: User) -> None:
        if hasattr(self.cmd, 'looping_users'):
            self.cmd.looping_users.pop(user.id, None)


    async def on_tip(self, sender, receiver, tip):
        await self.cmd.on_tip(sender, receiver, tip) 
        