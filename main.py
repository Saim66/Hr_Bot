import os
import asyncio
import logging
from dotenv import load_dotenv
from highrise import BaseBot, Position, User
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)
        # Pre-load data to prevent disk-hit during join
        self.data_cache = self.cmd.load_data()

    async def on_start(self, session_metadata):
        logger.info(f"✅ Bot Online: {session_metadata.room_info.room_name}")
        asyncio.create_task(self.emote_engine())
        asyncio.create_task(self.start_telegram())

    async def emote_engine(self):
        while True:
            if hasattr(self.cmd, 'looping_users') and self.cmd.looping_users:
                for user_id, official_id in list(self.cmd.looping_users.items()):
                    try:
                        await self.highrise.send_emote(official_id, user_id)
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Emote error: {e}")
            await asyncio.sleep(1)

    async def start_telegram(self):
        if not TELEGRAM_TOKEN: return
        try:
            app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
            async def tp_from_telegram(update, context):
                if update.effective_user.id != YOUR_TELEGRAM_ID: return
                if context.args:
                    await self.cmd.execute(None, context.args[0])
            app.add_handler(TG_Cmd("tp", tp_from_telegram))
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
        except Exception as e:
            logger.error(f"Telegram failed: {e}")

    async def on_chat(self, user, message: str) -> None:
        await self.cmd.execute(user, message)
        # Update cache when a command is executed
        self.data_cache = self.cmd.load_data()

    async def on_user_join(self, user: User):
        """Redesigned Join Handler: Uses a short delay to prevent disconnects."""
        await asyncio.sleep(1.5)  # Let the user settle before acting
        
        try:
            # Check bans
            if user.id in self.data_cache.get("restricted", []):
                await self.highrise.teleport(user.id, Position(0, 0, 0, "front-left"))
                return

            # Check VIP
            if user.id in self.data_cache.get("vips", []):
                await self.highrise.chat(f"Welcome back, VIP @{user.username}!")
                return

            # Welcome message
            welcomes = self.data_cache.get("welcomes", {})
            msg = welcomes.get(user.username.lower()) or "Welcome to the room!"
            await self.highrise.chat(f"@{user.username}, {msg}")
            
        except Exception as e:
            logger.error(f"Join event error: {e}")

    async def on_user_leave(self, user) -> None:
        if hasattr(self.cmd, 'looping_users'):
            self.cmd.looping_users.pop(user.id, None)