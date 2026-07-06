import asyncio
import json
import os
import importlib
from emotes import EMOTE_DICT

# ... (keep handle_command exactly as you have it) ...

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        
        # FIX: Get Room ID from env variable to make data files unique per bot
        room_id = os.getenv("ROOM_ID", "default_room")
        
        # Use a folder that persists (Railway Volume)
        self.data_dir = "/app/data"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
        
        # Unique filenames per bot/room
        self.data_file = os.path.join(self.data_dir, f"bot_data_{room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{room_id}.json")

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
            
    # ... (rest of your methods remain the same) ...


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