import asyncio
import json
import os
import importlib
from emotes import EMOTE_DICT

async def handle_command(handler_instance, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts: return
    
    # Remove "/" so "/help" becomes "help"
    trigger = parts[0].lstrip("/") 
    
    mapping = {
        "help": "help",
        "welcome": "welcome",
        "vip": "vip",
        "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation", "unban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", "clocs": "locations",
        "all": "emote_all",
        "wallet": "wallet",
        "tip": "tip",
        "welcome": "welcome",
        "stop": "loops", "0": "loops"
    }

    # 1. DYNAMIC LOCATION TELEPORT: Check if the command is a saved location
    if trigger in handler_instance.locations:
        module_name = "locations"
    
    # 2. STANDARD COMMANDS
    elif trigger in mapping:
        module_name = mapping[trigger]
    
    # 3. EMOTES
    elif trigger in EMOTE_DICT:
        module_name = "loops"
    
    else:
        module_name = None

    if module_name:
        try:
            module = importlib.import_module(f"commands.{module_name}")
            await module.execute(handler_instance, user, message)
        except Exception as e:
            print(f"Error executing {module_name}: {e}")

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "/app/data"
        self.data_file = os.path.join(self.data_dir, "bot_data.json")
        self.loc_file = os.path.join(self.data_dir, "locations.json")

        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
        self.tasks = {}
        self.data = self.load_data()
        self.locations = self.load_locations()
        self.looping_users = {}
        self.active_tasks = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"vips": [], "restricted": [], "welcomes": {}}

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def load_locations(self):
        if os.path.exists(self.loc_file):
            try:
                with open(self.loc_file, "r") as f:
                    return json.load(f)
            except: pass
        return {}

    def save_locations(self):
        with open(self.loc_file, "w") as f:
            json.dump(self.locations, f, indent=4)

    async def loop_emote(self, emote_id, target_id, target_name):
        self.looping_users[target_name] = True
        while self.looping_users.get(target_name, False):
            try:
                await self.bot.highrise.send_emote(emote_id, target_id)
                await asyncio.sleep(6)
            except Exception:
                break
        self.looping_users[target_name] = False
    
    async def stop_all_emotes(self, username):
        # Stop any active tasks for the given username
        if username in self.active_tasks:
            task = self.active_tasks[username]
            try:
                task.cancel()
            except Exception:
                pass
            del self.active_tasks[username]
        
        # Stop loop flag
        self.looping_users[username] = False
        return True
    
    async def execute(self, user, message: str) -> None:
        await handle_command(self, user, message)