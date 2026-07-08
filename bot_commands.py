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
    # Enforce prefix for everything
    if not msg.startswith("/"):
        return

    msg_lower = msg.lower()
    parts = msg_lower.split()
    if not parts: return
    
    trigger = parts[0].lstrip("/").lower()
    
    # Define routing
    mapping = {
        "help": "help", "welcome": "welcome", "setwelcome": "welcome",
        "vip": "vip", "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation", "unban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", 
        "clocs": "locations", "wallet": "wallet", "tip": "tip", 
        "stop": "loops", "0": "loops", "all": "loops"
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

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        room_id = os.getenv("ROOM_ID", "default_room")
        self.data_dir = "/app/data"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
        
        self.data_file = os.path.join(self.data_dir, f"bot_data_{room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{room_id}.json")
        self.data = self.load_data()
        self.locations = self.load_locations()
        self.active_tasks = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    if "custom_welcome" not in data: data["custom_welcome"] = ""
                    return data
            except: pass
        return {"vips": [], "restricted": [], "welcomes": {}, "custom_welcome": ""}

    def save_data(self):
        with open(self.data_file, "w") as f: json.dump(self.data, f, indent=4)

    def load_locations(self):
        if os.path.exists(self.loc_file):
            try:
                with open(self.loc_file, "r") as f: return json.load(f)
            except: pass
        return {}

    async def stop_user_loops(self, user):
        from commands.loops import stop_user_loops as stop_func
        await stop_func(self, user)

    async def execute(self, user, message: str) -> None:
        await handle_command(self, user, message)
