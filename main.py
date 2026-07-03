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

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)
        # Add a simple cache so we don't spam the disk
        self._last_load_time = 0 

    def get_data(self):
        """Only reload from disk if it hasn't been reloaded in the last 60 seconds."""
        import time
        if time.time() - self._last_load_time > 60:
            self.cmd.data = self.cmd.load_data()
            self._last_load_time = time.time()
        return self.cmd.data

    async def on_start(self, session_metadata): 
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
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
                    await self.highrise.chat(f"📱 Executing: {context.args[0]}")
                    await self.cmd.execute(None, context.args[0])
            
            app.add_handler(TG_Cmd("tp", tp_from_telegram))
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("✅ Telegram Controller Online.")
        except Exception as e:
            logger.error(f"❌ Telegram Controller failed: {e}")

    async def on_chat(self, user, message: str) -> None:
        await self.cmd.execute(user, message)

    async def on_user_join(self, user: User):
        # Use our cached data getter to keep the bot responsive
        data = self.get_data()
        
        # 1. Check BANS
        if user.id in data.get("restricted", []):
            await self.highrise.chat(f"@{user.username} is banned!")
            await self.highrise.teleport(user.id, Position(0, 0, 0, "front-left"))
            return

        # 2. Check VIP
        if user.id in data.get("vips", []):
            await self.highrise.chat(f"Welcome back, VIP @{user.username}!")
            return

        # 3. Custom Welcome
        welcomes = data.get("welcomes", {})
        msg = welcomes.get(user.username)
        if msg:
            await self.highrise.chat(f"@{user.username}, {msg}")
        else:
            await self.highrise.chat(f"Welcome to the room, @{user.username}!")

    async def on_user_leave(self, user) -> None:
        if hasattr(self.cmd, 'looping_users'):
            self.cmd.looping_users.pop(user.id, None)