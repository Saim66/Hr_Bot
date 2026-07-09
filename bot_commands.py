import asyncio
import json
import os
import importlib
import logging
from emotes import EMOTE_DICT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_command(handler_instance, user, message):
    msg = message.strip()
    if not msg:
        return
    
    parts = msg.split()
    trigger = parts[0].lstrip("/").lower()
    
    # 1. CENTRALIZED COMMAND MAPPING
    mapping = {
        "help": "help", "welcome": "welcome", "setwelcome": "welcome",
        "vip": "vip", "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation", "unban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", 
        "clocs": "locations", "wallet": "wallet", "tip": "tip", "tipall": "tip", 
        "stop": "loops", "0": "loops"
    }

    is_command = msg.startswith("/")
    is_emote = trigger in EMOTE_DICT
    is_location = trigger in handler_instance.locations

    # 2. ROUTING LOGIC
    # A) Explicit Slash Commands
    if is_command and trigger in mapping:
        module_name = mapping[trigger]
    # B) Location Teleport (Slash or No-Slash)
    elif is_location:
        module_name = "locations"
    # C) Emote Loops (No slash)
    elif not is_command and is_emote:
        module_name = "loops"
    else:
        # If command not found, return silently to prevent flooding logs
        return

    # 3. DYNAMIC EXECUTION
    try:
        # Ensure the module is reloaded if you change code while bot is running
        module = importlib.import_module(f"commands.{module_name}")
        importlib.reload(module) 
        await module.execute(handler_instance, user, message)
    except ModuleNotFoundError:
        logger.error(f"Module commands.{module_name} not found.")
    except Exception as e:
        logger.error(f"Error executing {module_name}: {e}")
        # Only chat if the bot has an active WebSocket connection
        if hasattr(handler_instance.bot.highrise, "ws") and handler_instance.bot.highrise.ws:
            await handler_instance.bot.highrise.chat(f"❌ System Error: {type(e).__name__}")

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.room_id = os.getenv("ROOM_ID", "default_room")
        self.data_dir = "/app/data"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
            
        self.data_file = os.path.join(self.data_dir, f"bot_data_{self.room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{self.room_id}.json")

        self.data = self.load_data()
        self.locations = self.load_locations()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f: return json.load(f)
            except: return {"vips": [], "restricted": [], "welcomes": {}}
        return {"vips": [], "restricted": [], "welcomes": {}}

    def load_locations(self):
        if os.path.exists(self.loc_file):
            try:
                with open(self.loc_file, "r") as f: return json.load(f)
            except: return {}
        return {}

    async def execute(self, user, message: str) -> None:
        # Always refresh state before execution to ensure accuracy
        self.locations = self.load_locations()
        await handle_command(self, user, message)
