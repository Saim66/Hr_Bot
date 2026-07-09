import json
import os
import importlib
import logging
from emotes import EMOTE_DICT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This handles the routing to your command files
async def handle_command(handler_instance, user, message):
    msg = message.strip()
    parts = msg.split()
    if not parts: return
    
    trigger = parts[0].lstrip("/").lower()
    
    mapping = {
        "help": "help", "welcome": "welcome", "setwelcome": "welcome",
        "restart": "owner", "shout": "owner", "emoteall": "owner",
        "vip": "vip", "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation", "unban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", 
        "clocs": "locations", "wallet": "wallet", "tip": "tip", "tipall": "tip", 
        "stop": "loops", "0": "loops"
    }

    is_command = msg.startswith("/")
    is_location = trigger in handler_instance.locations

    if is_command and trigger in mapping:
        module_name = mapping[trigger]
    elif is_command and is_location:
        module_name = "locations"
    elif not is_command and is_location:
        module_name = "locations"
    else:
        return

    try:
        module = importlib.import_module(f"commands.{module_name}")
        importlib.reload(module)
        await module.execute(handler_instance, user, message)
    except Exception as e:
        logger.error(f"Error executing {module_name}: {e}")
        try:
            await handler_instance.bot.highrise.chat(f"❌ Error in {module_name}: {str(e)[:40]}")
        except: pass

class CommandHandler:
    def __init__(self, bot, room_id):
        self.bot = bot
        self.room_id = room_id
        
        # Path to persistent Railway volume
        self.data_dir = "/var/lib/containers/railwayapp/bind-mounts/vol_iatnm6uo2p12iuk5"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
            
        # Namespaced files per room ID to prevent data conflicts
        self.data_file = os.path.join(self.data_dir, f"bot_data_{self.room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{self.room_id}.json")

        self.data = self.load_data()
        self.locations = self.load_locations()
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

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def save_locations(self):
        with open(self.loc_file, "w") as f:
            json.dump(self.locations, f, indent=4)

    async def execute(self, user, message: str) -> None:
        await handle_command(self, user, message)

    async def stop_user_loops(self, user):
        name = user.username.lower()
        if name in self.active_tasks:
            self.active_tasks[name]["task"].cancel()
            del self.active_tasks[name]
            logger.info(f"⏹️ Stopped loops for {name}")
