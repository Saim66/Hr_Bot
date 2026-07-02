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

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata) -> None:
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        # Start background tasks safely
        asyncio.create_task(self.start_telegram())
        asyncio.create_task(self.emote_engine())

    async def emote_engine(self):
        """Persistent loop engine. Keeps emotes running without crashing the bot."""
        while True:
            # We check the dict in commands.py
            if self.cmd.looping_users:
                # Use list() to prevent 'dictionary changed size' errors
                for user_id, emote_id in list(self.cmd.looping_users.items()):
                    try:
                        await self.highrise.send_emote(emote_id, user_id)
                    except Exception as e:
                        logger.warning(f"Emote loop error for {user_id}: {e}")
            
            # Wait 5 seconds before the next loop pass
            await asyncio.sleep(5)

    async def start_telegram(self):
        if not TELEGRAM_TOKEN:
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
        """
        GREETING LOGIC:
        Kept extremely simple to prevent connection drops/restarts.
        """
        logger.info(f"👤 User joined: {user.username}")
        try:
            # Short sleep helps prevent 'Rate Limit' kicks by Highrise servers
            await asyncio.sleep(1.5)
            await self.highrise.chat(f"Welcome @{user.username}! 👋")
        except Exception as e:
            logger.error(f"Error in on_user_join: {e}")