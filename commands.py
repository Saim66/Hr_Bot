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
            await self.bot.highrise.chat("📜 Commands: /welcome, /s, /to, /kick, /ban")
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
        if trigger == "/vip" and is_owner:
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
        
        if trigger in self.locations:
            # Permission check
            if trigger in self.data.get("restricted", []) and not is_owner:
                await self.bot.highrise.chat(f"🚫 Sorry @{user.username}, that is an Owner-only area!")
                return
            
            loc = self.locations[trigger]
            # Ensure the position is valid
            target_pos = Position(float(loc['x']), float(loc['y']), float(loc['z']), loc['facing'])
            await self.bot.highrise.teleport(user.id, target_pos)
            await self.bot.highrise.chat(f"🚀 Teleporting to {trigger}!")
            return
        
        # 7. SAVE LOCATION
        if trigger == "/set" and is_owner:
            if not args:
                await self.bot.highrise.chat("Usage: /set [name]")
                return
            
            loc_name = args[0].lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            
            # Find the owner's position
            my_pos = next((p for r, p in room_users if r.id == user.id), None)
            
            if my_pos:
                # Save to the locations dictionary
                self.locations[loc_name] = {
                    "x": my_pos.x, 
                    "y": my_pos.y, 
                    "z": my_pos.z, 
                    "facing": my_pos.facing
                }
                self.save_locations() # This saves it to locations.json
                await self.bot.highrise.chat(f"✅ Location '{loc_name}' saved permanently!")
            else:
                await self.bot.highrise.chat("❌ Could not get your current position.")
            return
        
        # 9. DELETE LOCATION
        if trigger in ["/dloc", "/deleteloc"] and is_owner:
            if not args:
                await self.bot.highrise.chat("Usage: /delloc [name]")
                return
            
            loc_name = args[0].lower()
            
            if loc_name in self.locations:
                del self.locations[loc_name]
                self.save_locations()
                await self.bot.highrise.chat(f"🗑️ Location '{loc_name}' has been deleted!")
            else:
                await self.bot.highrise.chat(f"❌ Location '{loc_name}' not found.")
            return
        
        # 8. CHECK SAVED LOCATIONS
        if trigger == "/clocs" and is_owner:
            if not self.locations:
                await self.bot.highrise.chat("📂 No locations are saved.")
            else:
                loc_list = ", ".join(self.locations.keys())
                await self.bot.highrise.chat(f"📂 Saved locations: {loc_list}")
            return
        
        # 10. EMOTE ALL
        if trigger == "/all" and is_owner and args:
            emote_name = args[0]
            room_users = (await self.bot.highrise.get_room_users()).content
            
            # Send emote to everyone in the room
            for user_obj, _ in room_users:
                try:
                    await self.bot.highrise.send_emote(emote_name, user_obj.id)
                except Exception:
                    continue # Skip if user cannot emote
            await self.bot.highrise.chat(f"✨ Emote '{emote_name}' sent to everyone!")
            return

        # 11. USER INFO
        if trigger == "/info" and is_vip and args:
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            
            if target:
                is_target_vip = target.username.lower() in self.data.get("vips", [])
                await self.bot.highrise.chat(
                    f"👤 @{target.username} | ID: {target.id} | VIP: {'Yes' if is_target_vip else 'No'}"
                )
            else:
                await self.bot.highrise.chat("❌ User not found in this room.")
            return
        
        # 12. EMOTE USER
        # Usage: /emote [emote_name] @[username]
        if trigger == "/emote" and is_vip:
            if len(args) < 2:
                await self.bot.highrise.chat("Usage: /emote [emote_name] @[username]")
                return
            
            emote_name = args[0]
            target_name = args[1].replace("@", "").lower()
            
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            
            if target:
                try:
                    await self.bot.highrise.send_emote(emote_name, target.id)
                    await self.bot.highrise.chat(f"✨ Emote '{emote_name}' sent to @{target.username}!")
                except Exception as e:
                    await self.bot.highrise.chat(f"⚠️ Could not emote: {str(e)}")
            else:
                await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
            return
        