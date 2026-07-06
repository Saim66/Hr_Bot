import os
import asyncio
import logging
from highrise import BaseBot, Position, User
from bot_commands import CommandHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        # Initialize user_id here so it exists from the start
        self.user_id = None 
        self.cmd = CommandHandler(self)
        self._api_lock = asyncio.Semaphore(1) 

    async def on_start(self, session_metadata):
        # Assign to user_id so your movement commands can find it
        self.user_id = session_metadata.user_id
        logger.info(f"✅ Bot Online in: {session_metadata.room_info.room_name}")
        asyncio.create_task(self.emote_engine())

    async def safe_api_call(self, coro):
        async with self._api_lock:
            try:
                return await coro
            except Exception as e:
                logger.warning(f"API call skipped: {e}")
                return None

    async def emote_engine(self):
        while True:
            # Check if looping_users exists and has items
            if hasattr(self.cmd, 'looping_users') and self.cmd.looping_users:
                for user_id, official_id in list(self.cmd.looping_users.items()):
                    await self.safe_api_call(self.highrise.send_emote(official_id, user_id))
                    await asyncio.sleep(2)
            await asyncio.sleep(1)

    async def on_chat(self, user: User, message: str) -> None:
        # Pass the message to your command handler
        await self.cmd.execute(user, message)

    async def on_user_join(self, user: User, position: Position) -> None:
        try:
            user_lower = user.username.lower()
            welcomes = self.cmd.data.get("welcomes", {})
            vips = self.cmd.data.get("vips", [])
            restricted = self.cmd.data.get("restricted", [])

            if user_lower in restricted:
                await self.highrise.teleport(user.id, Position(0, 0, 0, "FrontLeft"))
                return

            if user_lower in vips:
                await self.highrise.chat(f"👑 Welcome back, VIP @{user.username}!")
                return

            if user_lower in welcomes:
                final_msg = welcomes[user_lower].replace("{username}", user.username)
                await self.highrise.chat(f"👋 @{user.username}, {final_msg}")
            else:
                await self.highrise.chat(f"👋 Hello @{user.username}, welcome to the room!")

        except Exception as e:
            logger.error(f"CRITICAL ERROR in on_user_join: {e}")

    async def on_user_leave(self, user: User) -> None:
        if hasattr(self.cmd, 'looping_users'):
            self.cmd.looping_users.pop(user.id, None)

    async def on_tip(self, sender, receiver, tip):
        if hasattr(self.cmd, 'on_tip'):
            await self.cmd.on_tip(sender, receiver, tip)
