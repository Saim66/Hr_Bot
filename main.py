import asyncio
import logging
import os
from highrise import BaseBot, Position, User, CurrencyItem, Union, Item, SessionMetadata
from bot_commands import CommandHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        # FIX 1: Pass the room_id from Environment Variables
        room_id = os.getenv("ROOM_ID", "default_room")
        self.cmd = CommandHandler(self, room_id=room_id)
        self._api_lock = asyncio.Semaphore(1)

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.bot_id = session_metadata.user_id 
        logger.info(f"✅ Bot Online in: {session_metadata.room_info.room_name}")

    async def safe_api_call(self, coro):
        """Prevents the bot from crashing if an API call fails."""
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
            OWNER_USERNAME = "saim06" 
            
            # 1. SPECIAL OWNER WELCOME
            if user_lower == OWNER_USERNAME.lower():
                await self.highrise.chat(f"👑 Welcome back, Master @{user.username}!")
                await self.highrise.send_emote("emote-bow", user.id)
                return

            # 2. EXISTING LOGIC (VIPs / Restricted)
            vips = [v.lower() for v in self.cmd.data.get("vips", [])]
            restricted = [r.lower() for r in self.cmd.data.get("restricted", [])]

            if user_lower in restricted:
                await self.safe_api_call(self.highrise.teleport(user.id, Position(0, 0, 0, "FrontLeft")))
                return

            prefix = "👑 VIP" if user_lower in vips else "👋 Hello"
            await self.safe_api_call(self.highrise.chat(f"{prefix} @{user.username}, welcome to the room!"))

            # Custom Whisper Welcome
            custom = self.cmd.data.get("custom_welcome")
            if custom:
                await asyncio.sleep(2) 
                await self.safe_api_call(self.highrise.send_whisper(user.id, f"📜 Note: {custom}"))

        except Exception as e:
            logger.error(f"CRITICAL ERROR in on_user_join: {e}")

    async def on_user_leave(self, user: User) -> None:
        try:
            await self.cmd.stop_user_loops(user)
        except Exception as e:
            logger.error(f"Error in on_user_leave: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        # FIX 2: Cleaned up duplicated try/except blocks
        try:
            if hasattr(self.cmd, 'on_tip'):
                await self.cmd.on_tip(sender, receiver, tip)
        except Exception as e:
            logger.error(f"Error forwarding tip to handler: {e}")
