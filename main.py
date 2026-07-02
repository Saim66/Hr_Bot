import os
import asyncio
import logging
from highrise import BaseBot
from highrise import __main__
from dotenv import load_dotenv
from highrise import BaseBot, BotDefinition
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ROOM_ID = os.getenv("ROOM_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata) -> None:
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        # Start Telegram controller as a background task
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

async def main():
    # Use BotDefinition to wrap your custom Bot class for the SDK
    bot_def = BotDefinition(Bot)
    # The run method manages the connection to the Highrise server
    await bot_def.run(BOT_TOKEN, ROOM_ID)

# Replace the main() function and execution block with this:
if __name__ == "__main__":
    bot = Bot()
    # This uses the stable, older method to start the bot
    __main__.main(bot, BOT_TOKEN, ROOM_ID)