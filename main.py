import os
import asyncio
import logging
import json
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
        asyncio.create_task(self.emote_engine())

    # Inside main.py - emote_engine loop
async def emote_engine(self):
    while True:
        # Get a copy of the dictionary to avoid 'dictionary size changed' errors
        for user_id, official_id in list(self.cmd.looping_users.items()):
            # If the user was removed, this loop will naturally skip them
            await self.bot.highrise.send_emote(official_id, user_id)
            await asyncio.sleep(2) # adjust delay as needed
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

    async def on_user_join(self, user, position) -> None:
        logger.info(f"👤 User joined: {user.username}")
        try:
            await asyncio.sleep(1.5)
            
            # Load data to check for custom welcome message
            custom_msg = None
            if os.path.exists("bot_data.json"):
                with open("bot_data.json", "r") as f:
                    try:
                        data = json.load(f)
                        custom_msg = data.get("welcomes", {}).get(user.username.lower())
                    except: pass
            
            if custom_msg:
                await self.highrise.chat(f"@{user.username}, {custom_msg}")
            else:
                await self.highrise.chat(f"Welcome to the room, @{user.username}! 👋")
                
        except Exception as e:
            logger.error(f"Error in on_user_join: {e}")

    async def on_user_leave(self, user) -> None:
        # Cleanup if user was in an emote loop
        if user.id in self.cmd.looping_users:
            self.cmd.looping_users.pop(user.id, None)