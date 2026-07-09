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
    parts = msg.split()
    if not parts:
        return
    
    trigger = parts[0].lstrip("/").lower()
    
    # Mapping remains exactly as you had it
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

    # ROUTING LOGIC
    # Prioritize Commands -> Locations -> Emotes
    if is_command and trigger in mapping:
        module_name = mapping[trigger]
    elif is_command and is_location:
        module_name = "locations"
    elif not is_command and is_emote:
        module_name = "loops"
    elif not is_command and is_location:
        module_name = "locations"
    else:
        return

    try:
        # Dynamically import the module
        module = importlib.import_module(f"commands.{module_name}")
        
        # RELOAD logic added to ensure changes to tip.py take effect instantly
        importlib.reload(module)
        
        await module.execute(handler_instance, user, message)
    except Exception as e:
        logger.error(f"Error executing {module_name}: {e}")
        # Only chat if the websocket is active to prevent crashes
        if hasattr(handler_instance.bot.highrise, "ws") and handler_instance.bot.highrise.ws:
            # We truncate the error to ensure the chat message isn't too long
            await handler_instance.bot.highrise.chat(f"❌ Error in {module_name}: {str(e)[:40]}")

class CommandHandler:
    # (Your existing __init__ and data loading methods remain unchanged)
    def __init__(self, bot):
        self.bot = bot
        room_id = os.getenv("ROOM_ID", "default_room")
        self.data_dir = "/app/data"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
            
        self.data_file = os.path.join(self.data_dir, f"bot_data_{room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{room_id}.json")

        self.data = self.load_data()
        self.locations = self.load_locations()
        self.looping_users = {}
        self.active_tasks = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f: return json.load(f)
            except: pass
        return {"vips": [], "restricted": [], "welcomes": {}}

    def load_locations(self):
        if os.path.exists(self.loc_file):
            try:
                with open(self.loc_file, "r") as f: return json.load(f)
            except: pass
        return {}

    async def execute(self, user, message: str) -> None:
        self.locations = self.load_locations()
        await handle_command(self, user, message)
