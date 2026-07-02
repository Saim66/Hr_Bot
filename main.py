import os
import asyncio
import logging
from dotenv import load_dotenv
from highrise import BaseBot
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# Configure logging to see events in Railway console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Using the fallback provided in your previous message
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata) -> None:
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        # Start Telegram as a background task
        asyncio.create_task(self.start_telegram())

    async def start_telegram(self):
        """Initializes the Telegram remote control."""
        if not TELEGRAM_TOKEN:
            logger.error("❌ TELEGRAM_TOKEN not found! Telegram controller will not start.")
            return

        try:
            app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

            async def tp_from_telegram(update, context):
                if update.effective_user.id != YOUR_TELEGRAM_ID:
                    return
                
                if context.args:
                    cmd_name = context.args[0]
                    logger.info(f"📱 Telegram command received: {cmd_name}")
                    await self.highrise.chat(f"📱 Executing: {cmd_name}")
                    await self.cmd.execute(None, cmd_name)

            app.add_handler(TG_Cmd("tp", tp_from_telegram))
            
            logger.info("🚀 Initializing Telegram Controller...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("✅ Telegram Controller Online and polling.")
            
        except Exception as e:
            logger.error(f"❌ Telegram Controller failed to start: {e}")

    async def on_chat(self, user, message: str) -> None:
        logger.info(f"💬 Chat from {user.username}: {message}")
        await self.cmd.execute(user, message)

    async def on_user_join(self, user) -> None:
        logger.info(f"👤 User joined: {user.username}")

# This part is handled by the SDK, but ensure your Procfile runs the command correctly