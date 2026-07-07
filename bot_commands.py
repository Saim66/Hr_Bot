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
    
    # 1. CHECK FOR LOCATION FIRST (No prefix needed)
    if parts[0] in handler_instance.locations:
        module_name = "locations"
    # 2. CHECK FOR PREFIX COMMANDS
    else:
        trigger = parts[0].lstrip("/") 
        mapping = {
            "help": "help", "welcome": "welcome", "vip": "vip",
            "s": "movement", "to": "movement", "cords": "movement",
            "kick": "moderation", "ban": "moderation", "unban": "moderation",
            "set": "locations", "dloc": "locations", "deleteloc": "locations", "clocs": "locations",
            "all": "emote_all", "wallet": "wallet", "tip": "tip", "stop": "loops", "0": "loops"
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
        await handler_instance.bot.highrise.chat(f"❌ Error: {str(e)[:50]}")

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.all_loop_task = None # Global task for /all command
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

    async def loop_emote(self, emote_id, target_id, target_name):
        self.looping_users[target_name] = True
        while self.looping_users.get(target_name, False):
            try:
                await self.bot.highrise.send_emote(emote_id, target_id)
                await asyncio.sleep(6)
            except Exception: break
        self.looping_users[target_name] = False
    
    async def stop_all_emotes(self, username):
        """Stops both individual loops and the global /all loop."""
        # Stop individual user loop
        if username in self.looping_users:
            self.looping_users[username] = False
        
        # Stop global /all loop cleanly
        if self.all_loop_task:
            self.all_loop_task.cancel()
            try:
                await self.all_loop_task
            except asyncio.CancelledError:
                pass
            self.all_loop_task = None
        return True
    
    async def execute(self, user, message: str) -> None:
        await handle_command(self, user, message)
