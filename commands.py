import json
import os
from highrise import Position
import config
from emotes import EMOTE_DICT

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "/app/data"
        self.data_file = os.path.join(self.data_dir, "bot_data.json")
        self.loc_file = os.path.join(self.data_dir, "locations.json")
        
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
        
        self.data = self.load_data()
        self.locations = self.load_locations()
        self.looping_users = {}

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

    async def execute(self, user, message: str) -> None:
        if not user: return
        msg = message.strip().lower()
        parts = msg.split()
        if not parts: return
        
        trigger = parts[0]
        args = parts[1:]

        is_owner = user.username.lower() == config.OWNER_USERNAME.lower()
        is_vip = user.username.lower() in self.data.get("vips", []) or is_owner

        # 1. HELP
        if trigger == "/help":
            await self.bot.highrise.chat("📜 Commands: /welcome, /s, /to, /addvip, /kick, /ban")
            return

        # 2. WELCOME MANAGEMENT
        if trigger == "/welcome" and is_owner:
            if len(args) < 2:
                await self.bot.highrise.chat("Usage: /welcome @username message")
                return
            target = args[0].replace("@", "").lower()
            self.data["welcomes"][target] = " ".join(args[1:])
            self.save_data()
            await self.bot.highrise.chat(f"✅ Welcome set for @{target}")
            return

        # 3. VIP MANAGEMENT
        if trigger == "/addvip" and is_owner:
            if not args: return
            target = args[0].replace("@", "").lower()
            if target not in self.data["vips"]:
                self.data["vips"].append(target)
                self.save_data()
                await self.bot.highrise.chat(f"✅ @{target} added to VIPs.")
            else:
                await self.bot.highrise.chat(f"⚠️ @{target} is already a VIP.")
            return

        # 4. SUMMON & TELEPORT
        if trigger in ["/s", "/to"] and is_vip:
            if not args: return
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            
            if target:
                if trigger == "/s":
                    my_pos = next((p for r, p in room_users if r.id == user.id), None)
                    if my_pos: await self.bot.highrise.teleport(target.id, my_pos)
                else:
                    t_pos = next((p for r, p in room_users if r.id == target.id), None)
                    if t_pos: await self.bot.highrise.teleport(user.id, t_pos)
            else:
                await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
            return

        # 5. MODERATION
        if trigger in ["/kick", "/ban"] and is_owner:
            if not args: return
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            if target:
                await self.bot.highrise.moderate_room(target.id, trigger.replace("/", ""))
                await self.bot.highrise.chat(f"🚫 @{target.username} has been {trigger.replace('/', '')}ed.")
            else:
                await self.bot.highrise.chat("❌ User not found.")
            return

        # 6. EMOTE ENGINE
        if trigger in EMOTE_DICT:
            self.looping_users[user.id] = EMOTE_DICT[trigger]
            await self.bot.highrise.send_emote(EMOTE_DICT[trigger], user.id)
            return

        if trigger in ["stop", "0"]:
            self.looping_users.pop(user.id, None)
            await self.bot.highrise.send_emote("idle", user.id)
            await self.bot.highrise.chat(f"🛑 Stopped.")
            return