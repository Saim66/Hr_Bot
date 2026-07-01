import json
import os
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

        # --- 1. ADMIN COMMANDS (Prefix: /) ---
        if trigger.startswith(config.PREFIX):
            cmd = trigger[len(config.PREFIX):]

            if is_owner:
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
                        await self.bot.highrise.chat(f"💾 Saved location '{loc_name}'.")
                    return

                elif cmd == "del" and args:
                    loc_name = args[0].lower()
                    if os.path.exists("locations.json"):
                        with open("locations.json", "r", encoding="utf-8") as f: data = json.load(f)
                        if loc_name in data:
                            del data[loc_name]
                            with open("locations.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
                            await self.bot.highrise.chat(f"🗑️ Deleted '{loc_name}'.")
                    return

                elif cmd == "s" and args:
                    target_name = args[0].replace("@", "").lower()
                    room_users = (await self.bot.highrise.get_room_users()).content
                    owner_pos = next((pos for r, pos in room_users if r.id == user.id), None)
                    for r, _ in room_users:
                        if r.username.lower() == target_name and owner_pos:
                            await self.bot.highrise.teleport(r.id, owner_pos)
                            await self.bot.highrise.chat(f"✨ Summoned @{target_name}!")
                            return
            return

        # --- 2. SUMMON (No Prefix) ---
        if trigger == "s" and args and is_owner:
            target = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            owner_pos = next((pos for r, pos in room_users if r.id == user.id), None)
            for r, _ in room_users:
                if r.username.lower() == target and owner_pos:
                    await self.bot.highrise.teleport(r.id, owner_pos)
                    await self.bot.highrise.chat(f"✨ Summoned @{target}!")
                    return

        # --- 3. DIRECT TELEPORT (No Prefix) ---
        if os.path.exists("locations.json"):
            with open("locations.json", "r", encoding="utf-8") as f: 
                try: data = json.load(f)
                except: data = {}
            if trigger in data:
                l = data[trigger]
                await self.bot.highrise.teleport(user.id, Position(l['x'], l['y'], l['z'], l['facing']))
                await self.bot.highrise.chat(f"🚀 Warping @{user.username} to {trigger}!")
                return

        # --- 4. EMOTE ENGINE ---
        if trigger in EMOTE_DICT:
            eid = EMOTE_DICT[trigger]
            target_id = user.id
            if args:
                target_name = args[0].replace("@", "").lower()
                room_users = (await self.bot.highrise.get_room_users()).content
                found = next((r for r, _ in room_users if r.username.lower() == target_name), None)
                if found: target_id = found.id
            
            self.looping_users[target_id] = eid
            await self.bot.highrise.send_emote(eid, target_id)
            await self.bot.highrise.chat(f"💃 Emote loop started!")
            return