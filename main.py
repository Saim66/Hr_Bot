import os
import asyncio
import logging
from dotenv import load_dotenv
from highrise import BaseBot, Highrise
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Combined and cleaned up startup logs
        print("DEBUG: on_start triggered", flush=True)
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        asyncio.create_task(self.start_telegram())

    async def start_telegram(self):
        # ... (keep your existing Telegram logic here) ...
        try:
            app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
            # ... (add handlers) ...
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("✅ Telegram Controller Online and polling.")
        except Exception as e:
            logger.error(f"❌ Telegram Controller failed to start: {e}")

    async def on_chat(self, user, message: str) -> None:
        await self.cmd.execute(user, message)

# --- THIS IS THE MISSING PART ---
async def main():
    bot = Bot()
    async with Highrise() as h:
        await h.run(BOT_TOKEN, ROOM_ID, bot)

if __name__ == "__main__":
    asyncio.run(main())