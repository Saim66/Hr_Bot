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
        self.data_file = "bot_data.json"
        self.loc_file = "locations.json"
        self.data = {"vips": [], "welcomes": {}, "restricted": []}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try: self.data = json.load(f)
                except: pass

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    async def execute(self, user, message: str) -> None:
        if not user: return
        msg = message.strip()
        parts = msg.split()
        trigger = parts[0].lower()
        args = parts[1:]
        
        is_owner = user.username.lower() == config.OWNER_USERNAME.lower()
        is_vip = user.username.lower() in self.data.get("vips", []) or is_owner

        # --- HELP ---
        if trigger == "/help":
            await self.bot.highrise.chat(f"📜 @{user.username}, available: /welcome [msg], /stop. VIPs: /to @user. Owner: /addvip, /kick, /ban, /ownergo [name]")
            return

        # --- CUSTOM WELCOME ---
        if trigger == "/welcome" and args:
            self.data["welcomes"][user.username.lower()] = " ".join(args)
            self.save_data()
            await self.bot.highrise.chat(f"✅ @{user.username}, your welcome message is set!")
            return

        # --- 2. STOP COMMAND (No prefix) ---
        # Now you can just type 'stop' or '0' in chat
        if trigger in ["stop", "0"]:
            self.looping_users.pop(user.id, None)
            await self.bot.highrise.chat(f"🛑 @{user.username}, stopped your emote loop.")
            return

        # --- 2. SUMMON COMMAND (/s @user) (Owner Only) ---
        if trigger == "/s" and is_vip and args:
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            owner_pos = next((p for r, p in room_users if r.id == user.id), None)
            
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            if target and owner_pos:
                await self.bot.highrise.teleport(target.id, owner_pos)
                await self.bot.highrise.chat(f"✨ Summoned @{target.username} to your side!")
            else:
                await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
            return

        # --- VIP: TELEPORT TO USER ---
        if trigger == "to" and is_vip and args:
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            if target:
                pos = next((p for r, p in room_users if r.id == target.id), None)
                await self.bot.highrise.teleport(user.id, pos)
                await self.bot.highrise.chat(f"🚀 Teleporting @{user.username} to @{target.username}")
            else:
                await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
            return

        # --- OWNER: MANAGE VIP ---
        if trigger == "/vip" and is_owner and args:
            vip_name = args[0].replace("@", "").lower()
            if vip_name not in self.data["vips"]:
                self.data["vips"].append(vip_name)
                self.save_data()
                await self.bot.highrise.chat(f"✅ @{vip_name} is now a VIP!")
            return
        
        # --- OWNER: LIST ALL VIPS ---
        if trigger == "/lvip" and is_owner:
            if not self.data["vips"]:
                await self.bot.highrise.chat("💎 The VIP list is currently empty.")
            else:
                vip_list = ", ".join([f"@{v}" for v in self.data["vips"]])
                await self.bot.highrise.chat(f"💎 VIP List: {vip_list}")
            return
            return
        
        # --- OWNER: REMOVE VIP ---
        if trigger == "/dvip" and is_owner and args:
            vip_name = args[0].replace("@", "").lower()
            if vip_name in self.data["vips"]:
                self.data["vips"].remove(vip_name)
                self.save_data()
                await self.bot.highrise.chat(f"❌ @{vip_name} has been removed from the VIP list.")
            else:
                await self.bot.highrise.chat(f"⚠️ @{vip_name} was not on the VIP list.")
            return
            

        # --- OWNER: MODERATION ---
        if trigger in ["/kick", "/ban"] and is_owner and args:
            target_name = args[0].replace("@", "").lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            if target:
                mode = "kick" if trigger == "/kick" else "ban"
                await self.bot.highrise.moderate_room(target.id, mode)
                await self.bot.highrise.chat(f"🚫 @{target.username} has been {mode}ed by @{user.username}")
            return

        # --- OWNER: SAVE AND RESTRICT LOCATION ---
        if trigger == "/own" and is_owner and args:
            loc_name = args[0].lower()
            
            # Get your current position
            room_users = (await self.bot.highrise.get_room_users()).content
            my_pos = next((p for r, p in room_users if r.id == user.id), None)
            
            if my_pos:
                # Load existing locations
                if os.path.exists(self.loc_file):
                    with open(self.loc_file, "r") as f:
                        try: locs = json.load(f)
                        except: locs = {}
                else:
                    locs = {}
                
                # Save the new coordinate
                locs[loc_name] = {
                    "x": my_pos.x,
                    "y": my_pos.y,
                    "z": my_pos.z,
                    "facing": my_pos.facing
                }
                
                with open(self.loc_file, "w") as f:
                    json.dump(locs, f, indent=4)
                
                # Add to restricted list
                if loc_name not in self.data["restricted"]:
                    self.data["restricted"].append(loc_name)
                    self.save_data()
                
                await self.bot.highrise.chat(f"📍 Location '{loc_name}' saved and restricted!")
            else:
                await self.bot.highrise.chat("❌ Could not get your current position.")
            return

        # --- EMOTE ENGINE ---
        if trigger in EMOTE_DICT or trigger.startswith(("emote-", "gacha-")):
            official_id = EMOTE_DICT.get(trigger, trigger)
            self.looping_users[user.id] = official_id
            await self.bot.highrise.send_emote(official_id, user.id)
            await self.bot.highrise.chat(f"💃 Starting emote for @{user.username}!")
            return
        

        # --- TARGETED EMOTE (e.g., "laid @user") ---
        # Normalize to lowercase so 'Laid' or 'laid' both work
        if len(parts) == 2 and parts[0].lower() in EMOTE_DICT and parts[1].startswith("@"):
            emote_name = parts[0].lower()
            target_name = parts[1].replace("@", "").lower()
            
            # Find the user
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            
            if target:
                official_id = EMOTE_DICT.get(emote_name)
                await self.bot.highrise.send_emote(official_id, target.id)
            else:
                await self.bot.highrise.chat(f"❌ User @{target_name} not found.")
            return

        # --- DIRECT LOCATION TELEPORT ---
        if os.path.exists(self.loc_file):
            with open(self.loc_file, "r") as f:
                try: locs = json.load(f)
                except: locs = {}
            if trigger in locs:
                if trigger in self.data.get("restricted", []) and not is_owner:
                    await self.bot.highrise.chat(f"🚫 Sorry @{user.username}, that is an Owner-only area!")
                    return
                l = locs[trigger]
                target_pos = Position(float(l['x']), float(l['y']), float(l['z']), l['facing'])
                await self.bot.highrise.teleport(user.id, target_pos)
                await self.bot.highrise.chat(f"🚀 Teleporting @{user.username} to {trigger}")