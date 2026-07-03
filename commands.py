import json
import os
import asyncio
from highrise import Position
import config
from emotes import EMOTE_DICT

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.loc_file = os.path.join(base_dir, "locations.json")
        self.data_file = os.path.join(base_dir, "bot_data.json")
        self.data_file = "/app/data/bot_data.json" # <--- Check this path
        self.data = {"vips": [], "welcomes": {}}
        self.loc_file = "locations.json"
        self.data_file = "bot_data.json"
        self.looping_users = {}
        
        # These methods must exist for these lines to work!
        self.locations = self.load_locations()
        self.data = self.load_data()

    # --- Add these methods INSIDE the class ---
    def load_locations(self):
        if os.path.exists(self.loc_file):
            with open(self.loc_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def load_data(self):
        # List everything in the root directory
        files_in_root = os.listdir('.')
        # List everything in the /app/data directory if it exists
        files_in_data = os.listdir('/app/data') if os.path.exists('/app/data') else "Folder does not exist"
        
        # Send this info to the chat so you can see it
        # We limit the output so it fits in one chat message
        response = f"Root: {files_in_root[:5]} | Data: {files_in_data}"
        
        # You can replace the chat call with print() if you prefer checking logs
        # await self.bot.highrise.chat(f"Files: {response}") 
        print(f"DEBUG: Files in root: {files_in_root}")
        print(f"DEBUG: Files in /app/data: {files_in_data}")
        # 1. Check if the file exists
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"vips": [], "restricted": [], "welcomes": {}}
        
        # 2. If it doesn't exist, create it so you don't keep getting "File not found"
        print(f"DEBUG: File not found at {self.data_file}, creating new one.")
        initial_data = {"vips": [], "restricted": [], "welcomes": {}}
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Save the default data
        with open(self.data_file, "w") as f:
            json.dump(initial_data, f)
            
        return initial_data

    def save_locations(self):
        with open(self.loc_file, "w") as f:
            json.dump(self.locations, f, indent=4)

    def save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=4)
            print(f"DEBUG: Successfully wrote to {self.data_file}")
            print(f"DEBUG: Current Data: {self.data}")
        except Exception as e:
            print(f"DEBUG: ERROR SAVING FILE: {e}")

    def add_vip(self, user_name):
        user_name = user_name.replace("@", "").lower()
        if user_name not in self.data["vips"]:
            self.data["vips"].append(user_name)
            self.save_data() # <--- Calling this triggers the write
            return True
        return False

    # Add this inside your CommandHandler class in commands.py
    async def check_data(self, user):
        try:
            # Point to the exact path of your volume
            path = "/app/data/bot_data.json"
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                    await self.bot.highrise.chat(f"Stored Data: {content}")
            else:
                await self.bot.highrise.chat("File not found! Check your path.")
        except Exception as e:
            await self.bot.highrise.chat(f"Error: {e}")    

    async def execute(self, user, message: str) -> None:
        if not user: return
        msg = message.strip()
        parts = msg.split()
        trigger = parts[0].lower()
        args = parts[1:]
        if message == "/checkdata":
            await self.check_data(user)
        
        is_owner = user.username.lower() == config.OWNER_USERNAME.lower()
        is_vip = user.username.lower() in self.data.get("vips", []) or is_owner

        # --- HELP ---
        if trigger == "/help":
            await self.bot.highrise.chat(f"📜 @{user.username}, available: /welcome [msg], /stop. , /s @user, /to @user. ")
            return

        # --- CUSTOM WELCOME ---
        if trigger == "/welcome" and is_owner:
            # 1. ADD THIS CHECK FIRST
            if "welcomes" not in self.data:
                self.data["welcomes"] = {}
            
            # 2. Now it is safe to add the user
            if len(args) >= 2:
                target_user = args[0].replace("@", "").lower()
                custom_message = " ".join(args[1:])
                
                self.data["welcomes"][target_user] = custom_message
                self.save_data() 
                
                await self.bot.highrise.chat(f"✅ Welcome message set for @{target_user}")
                return

        # --- 2. STOP COMMAND ---
        if trigger in ["stop", "0"]:
            # 1. Remove them from the tracking dictionary immediately
            self.looping_users.pop(user.id, None)
            
            # 2. Tell the Highrise API to stop the current emote
            # This sends an empty string or "stop" to clear the emote loop
            await self.bot.highrise.send_emote("idle", user.id)
            
            # 3. Inform the user
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
        if trigger == "/to" and is_vip and args:
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

        # Example of how your command trigger should look:
        if trigger == "/addvip" and is_owner and args:
            vip_name = args[0]
            # Call the function you just created
            success = self.add_vip(vip_name) 
            
            if success:
                await self.bot.highrise.chat(f"✅ @{vip_name} added to VIP list.")
            else:
                await self.bot.highrise.chat(f"⚠️ @{vip_name} is already a VIP.")
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

        # --- OWNER: SAVE LOCATION ---
        if trigger == "/own" and is_owner and args:
            loc_name = args[0].lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            my_pos = next((p for r, p in room_users if r.id == user.id), None)
            
            if my_pos:
                # Save to the locations dictionary
                self.locations[loc_name] = {
                    "x": my_pos.x,
                    "y": my_pos.y,
                    "z": my_pos.z,
                    "facing": my_pos.facing
                }
                # Save to file immediately
                self.save_locations()
                
                # Mark as restricted
                if loc_name not in self.data["restricted"]:
                    self.data["restricted"].append(loc_name)
                    self.save_data()
                
                await self.bot.highrise.chat(f"✅ Location '{loc_name}' saved and restricted!")
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
        
        # --- OWNER/VIP: SAVE PUBLIC LOCATION (/set) ---
        if trigger == "/set" and is_vip and args:
            loc_name = args[0].lower()
            room_users = (await self.bot.highrise.get_room_users()).content
            my_pos = next((p for r, p in room_users if r.id == user.id), None)
            
            if my_pos:
                self.locations[loc_name] = {
                    "x": my_pos.x, "y": my_pos.y, "z": my_pos.z, "facing": my_pos.facing
                }
                self.save_locations() # Saves to locations.json
                await self.bot.highrise.chat(f"📍 Location '{loc_name}' saved!")
            return

        # --- OWNER/VIP: DELETE LOCATION (/del) ---
        if trigger == "/del" and is_vip and args:
            loc_name = args[0].lower()
            if loc_name in self.locations:
                del self.locations[loc_name]
                self.save_locations() # Updates file
                await self.bot.highrise.chat(f"❌ Location '{loc_name}' has been deleted.")
            else:
                await self.bot.highrise.chat(f"⚠️ Location '{loc_name}' does not exist.")
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