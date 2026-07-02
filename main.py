import os
import asyncio
import logging
from dotenv import load_dotenv
from highrise import BaseBot
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata) -> None:
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        # Start background tasks
        asyncio.create_task(self.start_telegram())
        asyncio.create_task(self.emote_engine()) # <--- Engine activated

    async def emote_engine(self):
        """Ultra-reliable loop engine."""
        while True:
            # Always use a copy of the dictionary
            tasks = list(self.cmd.looping_users.items())
            
            for user_id, emote_id in tasks:
                try:
                    await self.highrise.send_emote(emote_id, user_id)
                except Exception as e:
                    # If one emote fails, we log it but DON'T stop the engine
                    logger.error(f"Looping failed for {user_id}: {e}")
            
            # Wait 5 seconds
            await asyncio.sleep(5)

    async def start_telegram(self):
        if not TELEGRAM_TOKEN:
            logger.error("❌ TELEGRAM_TOKEN not found!")
            return
        try:
            app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
            async def tp_from_telegram(update, context):
                if update.effective_user.id != YOUR_TELEGRAM_ID:
                    return
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

    async def on_user_join(self, user) -> None:
        logger.info(f"👤 User joined: {user.username}")
        try:
            # Keep welcome messages simple to avoid connection issues
            await self.highrise.chat(f"Welcome @{user.username}! 👋")
        except Exception as e:
            logger.error(f"Error in on_user_join: {e}")