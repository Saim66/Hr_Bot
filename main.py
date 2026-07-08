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
        self.cmd = CommandHandler(self)
        self._api_lock = asyncio.Semaphore(1)

    async def on_start(self, session_metadata):
        logger.info(f"✅ Bot Online in: {session_metadata.room_info.room_name}")

    async def safe_api_call(self, coro):
        async with self._api_lock:
            try:
                return await coro
            except Exception as e:
                logger.warning(f"API call skipped: {e}")
                return None

    async def on_chat(self, user: User, message: str) -> None:
        await self.cmd.execute(user, message)

    async def on_user_join(self, user: User, position: Position) -> None:
        try:
            user_lower = user.username.lower()
            vips = [v.lower() for v in self.cmd.data.get("vips", [])]
            restricted = [r.lower() for r in self.cmd.data.get("restricted", [])]

            # Restricted handling
            if user_lower in restricted:
                await self.highrise.teleport(user.id, Position(0, 0, 0, "FrontLeft"))
                return

            # Welcome Logic
            prefix = "👑 VIP" if user_lower in vips else "👋 Hello"
            await self.highrise.chat(f"{prefix} @{user.username}, welcome to the room!")

            # Custom Whisper Welcome
            custom = self.cmd.data.get("custom_welcome")
            if custom:
                await asyncio.sleep(2) # Give it a moment after chat
                await self.highrise.send_whisper(user.id, f"📜 Note: {custom}")

        except Exception as e:
            logger.error(f"CRITICAL ERROR in on_user_join: {e}")

    async def on_user_leave(self, user: User) -> None:
        # Clean up loops on leave
        await self.cmd.stop_user_loops(None, user)

    async def on_tip(self, sender: User, receiver: User, tip):
        # Forward tip logic to handler
        if hasattr(self.cmd, 'on_tip'):
            await self.cmd.on_tip(sender, receiver, tip)
