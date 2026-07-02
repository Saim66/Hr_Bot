import os
from dotenv import load_dotenv
import asyncio
from highrise import BaseBot
from commands import CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler as TG_Cmd

# --- CONFIGURATION ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_TELEGRAM_ID =int(os.getenv("YOUR_TELEGRAM_ID", "7241289551"))

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.cmd = CommandHandler(self)
        self.bot_id = None

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"✅ Highrise Bot Online! ID: {self.bot_id}")
        
        # Start Telegram bridge as a background task
        asyncio.create_task(self.start_telegram())

    async def start_telegram(self):
        """Initializes the Telegram remote control."""
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        async def tp_from_telegram(update, context):
            # Only allow your specific ID to control the bot
            if update.effective_user.id != YOUR_TELEGRAM_ID:
                return
            
            if context.args:
                cmd_name = context.args[0]
                await self.highrise.chat(f"📱 Remote command: {cmd_name}")
                await self.cmd.execute(None, cmd_name)

        app.add_handler(TG_Cmd("tp", tp_from_telegram))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print("✅ Telegram Controller Online.")

    async def on_chat(self, user, message: str) -> None:
        # Pass the Highrise user and message to your commands handler
        await self.cmd.execute(user, message)