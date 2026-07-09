import asyncio
import json
import os
import importlib
@@ -14,13 +13,12 @@ async def handle_command(handler_instance, user, message):
    parts = msg.split()
    if not parts: return

    # Check if slash command or direct teleport
    trigger = parts[0].lstrip("/").lower()

    mapping = {
        "help": "help", "welcome": "welcome", "setwelcome": "welcome",
        "restart": "owner",
        "shout": "owner",
        "emoteall": "owner",
        "restart": "owner", "shout": "owner", "emoteall": "owner",
        "vip": "vip", "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation", "unban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", 
@@ -45,7 +43,7 @@ async def handle_command(handler_instance, user, message):

    try:
        module = importlib.import_module(f"commands.{module_name}")
        importlib.reload(module) # Ensure code updates apply immediately
        importlib.reload(module)
        await module.execute(handler_instance, user, message)
    except Exception as e:
        logger.error(f"Error executing {module_name}: {e}")
@@ -57,11 +55,12 @@ class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        room_id = os.getenv("ROOM_ID", "default_room")
        self.data_dir = "/app/data"
        # Use your persistent path here
        self.data_dir = "/var/lib/containers/railwayapp/bind-mounts/vol_iatnm6uo2p12iuk5"
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)

        self.data_file = os.path.join(self.data_dir, f"bot_data_{room_id}.json")
        self.loc_file = os.path.join(self.data_dir, f"locations_{room_id}.json")
        self.data_file = os.path.join(self.data_dir, "bot_data.json")
        self.loc_file = os.path.join(self.data_dir, "locations.json")

        self.data = self.load_data()
        self.locations = self.load_locations()
@@ -81,17 +80,22 @@ def load_locations(self):
            except: pass
        return {}

    def save_data(self):
        """Saves VIPs and other settings to the persistent volume."""
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def save_locations(self):
        """Saves teleports to the persistent volume."""
        with open(self.loc_file, "w") as f:
            json.dump(self.locations, f, indent=4)

    async def execute(self, user, message: str) -> None:
        self.locations = self.load_locations()
        await handle_command(self, user, message)

    # FIXED: Added this method to the class so on_user_leave can find it
    async def stop_user_loops(self, user):
        name = user.username.lower()
        if name in self.active_tasks:
            data = self.active_tasks[name]
            # Cancel the task
            data["task"].cancel()
            # Clean up tracking
            self.active_tasks[name]["task"].cancel()
            del self.active_tasks[name]
            logger.info(f"⏹️ Stopped loops for {name}")
