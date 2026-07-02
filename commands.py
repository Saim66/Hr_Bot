import json
import os
import asyncio
from highrise import Position
import config
from emotes import EMOTE_DICT

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.looping_users = {}

    async def execute(self, user, message: str) -> None:
        msg = message.strip()
        if not msg: return
        is_owner = user.username.lower() == config.OWNER_USERNAME.lower()
        parts = msg.split()
        trigger = parts[0].lower()
        args = parts[1:]



        # --- DIRECT TELEPORT (No Prefix) ---
        if os.path.exists("locations.json"):
            with open("locations.json", "r", encoding="utf-8") as f: 
                try: data = json.load(f)
                except: data = {}
            
            if trigger in data:
                l = data[trigger]
                # target_pos is the destination
                target_pos = Position(float(l['x']), float(l['y']), float(l['z']), l['facing'])
                
                try:
                    # user.id teleports the PERSON who typed the command
                    await self.bot.highrise.teleport(user.id, target_pos)
                    await self.bot.highrise.chat(f"🚀 Teleporting @{user.username} to {trigger}!")
                except Exception as e:
                    print(f"Teleport Error: {e}")
                    await self.bot.highrise.chat(f"❌ Failed to teleport you. Check permissions.")
                return

        # --- 1. ADMIN COMMANDS (Prefix: /) ---
        if trigger.startswith(config.PREFIX):
            cmd = trigger[len(config.PREFIX):]

            if is_owner:
                # /set [name]
                if cmd == "set" and args:
                    loc_name = args[0].lower()
                    room_users = (await self.bot.highrise.get_room_users()).content
                    pos = next((p for r, p in room_users if r.id == user.id), None)
                    if pos:
                        data = {}
                        if os.path.exists("locations.json"):
                            with open("locations.json", "r", encoding="utf-8") as f:
                                try: data = json.load(f)
                                except: pass
                        data[loc_name] = {"x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing}
                        with open("locations.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)
                        await self.bot.highrise.chat(f"💾 Saved location as '{loc_name}'.")
                    return

                # /del [name]
                elif cmd == "del" and args:
                    loc_name = args[0].lower()
                    if os.path.exists("locations.json"):
                        with open("locations.json", "r", encoding="utf-8") as f: data = json.load(f)
                        if loc_name in data:
                            del data[loc_name]
                            with open("locations.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
                            await self.bot.highrise.chat(f"🗑️ Deleted location '{loc_name}'.")
                        else:
                            await self.bot.highrise.chat(f"ℹ️ Location '{loc_name}' not found.")
                    return
                
                # /s [user]
                elif cmd == "s" and args:
                    target = args[0].replace("@", "").lower()
                    room_users = (await self.bot.highrise.get_room_users()).content
                    owner_pos = next((pos for r, pos in room_users if r.id == user.id), None)
                    for r, _ in room_users:
                        if r.username.lower() == target and owner_pos:
                            await self.bot.highrise.teleport(r.id, owner_pos)
                            await self.bot.highrise.chat(f"✨ Summoned @{target} to your side!")
                            return
                    await self.bot.highrise.chat(f"❌ User @{target} not found.")
                    return
            return

        

        # --- 3. EMOTE / LOOP ENGINE ---
        if trigger in EMOTE_DICT or trigger.startswith(("emote-", "gacha-")):
            official_id = EMOTE_DICT.get(trigger, trigger)
            target_id = user.id
            target_name = user.username

            if args:
                target_name = args[0].replace("@", "").lower()
                room_users = (await self.bot.highrise.get_room_users()).content
                found = next((r for r, _ in room_users if r.username.lower() == target_name), None)
                if found:
                    target_id = found.id
                else:
                    await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
                    return
            
            self.looping_users[target_id] = official_id
            await self.bot.highrise.send_emote(official_id, target_id)
            await self.bot.highrise.chat(f"💃 Emote loop started for @{target_name}!")
            return

        # 4. STOP LOOP
        if trigger in ["stop", "s", "0"]:
            if user.id in self.looping_users:
                self.looping_users.pop(user.id, None)
                await self.bot.highrise.chat(f"🛑 Stopped your emote loop.")

        # --- 2. DIRECT TELEPORT (No Prefix) ---
        if os.path.exists("locations.json"):
            with open("locations.json", "r", encoding="utf-8") as f: 
                try: data = json.load(f)
                except: data = {}
            
            if trigger in data:
                l = data[trigger]
                # Force the coordinate objects
                target_pos = Position(float(l['x']), float(l['y']), float(l['z']), l['facing'])
                
                # Use the bot's highrise instance directly
                try:
                    await self.bot.highrise.teleport(user.id, target_pos)
                    await self.bot.highrise.chat(f"🚀 Teleporting you to {trigger}!")
                except Exception as e:
                    print(f"DEBUG ERROR: {e}")
                    await self.bot.highrise.chat(f"⚠️ Error: Could not move you.")
                return