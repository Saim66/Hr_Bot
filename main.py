import os
import asyncio
import logging
import json
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
        # This connects all your commands from commands.py
        self.cmd = CommandHandler(self)

    async def on_start(self, session_metadata): 
        logger.info(f"✅ Highrise Bot Online! Room: {session_metadata.room_info.room_name}")
        # Start background tasks
        asyncio.create_task(self.emote_engine())
        asyncio.create_task(self.start_telegram())

    async def emote_engine(self):
        """Looping emote engine for all added users."""
        while True:
            # We access looping_users from your command handler
            if self.cmd.looping_users:
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
        # All your existing commands in commands.py will work through this
        await self.cmd.execute(user, message)

    async def on_user_join(self, user: User): # Removed room: RoomUser
        # Now we only use user.id, which is all we need!
        
        # 1. Check if user is restricted (Banned)
        if user.id in self.cmd.data.get("restricted", []):
            try:
                # Teleport user to a safe exit position
                await self.highrise.teleport(user.id, Position(x=0, y=0, z=0, facing="FrontLeft"))
                await self.highrise.chat(f"@{user.username} is banned from this room.")
            except Exception as e:
                print(f"Error teleporting banned user: {e}")
            return

        # 2. Check if user is VIP
        if user.id in self.cmd.data.get("vips", []):
            await self.highrise.chat(f"Welcome back, VIP @{user.username}!")

    async def on_user_leave(self, user) -> None:
        # Cleanup loop if user leaves
        self.cmd.looping_users.pop(user.id, None)