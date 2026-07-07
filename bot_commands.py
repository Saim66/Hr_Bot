import asyncio
import json
import os
import importlib
import logging
from emotes import EMOTE_DICT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_command(handler_instance, user, message):
    msg = message.strip()
    msg_lower = msg.lower()
    parts = msg_lower.split()
    if not parts: return
    
    # 1. CHECK FOR LOCATION FIRST
    if parts[0] in handler_instance.locations:
        module_name = "locations"
    # 2. CHECK FOR PREFIX COMMANDS
    else:
        trigger = parts[0].lstrip("/") 
        mapping = {
            "help": "help", "welcome": "welcome", "vip": "vip",
            "s": "movement", "to": "movement", "cords": "movement",
            "kick": "moderation", "ban": "moderation", "unban": "moderation",
            "set": "locations", "dloc": "locations", "deleteloc": "locations", 
            "clocs": "locations", "wallet": "wallet", "tip": "tip", 
            "stop": "loops", "0": "loops", "all": "loops" # Added 'all' here
        }
        
        if trigger in mapping:
            module_name = mapping[trigger]
        elif trigger in EMOTE_DICT:
            module_name = "loops"
        else:
            return

    try:
        module = importlib.import_module(f"commands.{module_name}")
        await module.execute(handler_instance, user, message)
    except Exception as e:
        logger.error(f"Error executing {module_name}: {e}")
        # Only chat if the connection is active to avoid crashes
        if handler_instance.bot.highrise.ws and not handler_instance.bot.highrise.ws.closed:
            await handler_instance.bot.highrise.chat(f"❌ Error: {str(e)[:50]}")

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.all_loop_task = None 
        room_id = os.getenv("ROOM_ID", "default_room")
        self.data_dir = "/app/data"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
            
        self.data_file = os.path.join(self.data_dir, f"bot_data_{room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{room_id}.json")

        self.data = self.load_data()
        self.locations = self.load_locations()
        
        # Unified tracking
        self.looping_users = {}
        self.active_tasks = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f: return json.load(f)
            except: pass
        return {"vips": [], "restricted": [], "welcomes": {}}

    def save_data(self):
        with open(self.data_file, "w") as f: json.dump(self.data, f, indent=4)

    def load_locations(self):
        if os.path.exists(self.loc_file):
            try:
                with open(self.loc_file, "r") as f: return json.load(f)
            except: pass
        return {}

    def save_locations(self):
        with open(self.loc_file, "w") as f: json.dump(self.locations, f, indent=4)
    
    async def execute(self, user, message: str) -> None:
        await handle_command(self, user, message)
