import asyncio
import json
import os
from typing import Union  # Added this for the tip function
from highrise import Position, User, CurrencyItem, Item
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
        self.active_tasks = {}

    async def loop_emote(self, emote_id, target_id, target_name):
        self.looping_users[target_name] = True
        print(f"DEBUG: Starting loop for {target_name} with {emote_id}")
        
        while self.looping_users.get(target_name, False):
            try:
                await self.bot.highrise.send_emote(emote_id, target_id)
                await asyncio.sleep(6) # Emote duration
            except Exception as e:
                print(f"DEBUG: Error in loop: {e}")
                break
        
        self.looping_users[target_name] = False

    # Using strings ("User", "CurrencyItem") avoids the NameError
    async def on_tip(self, sender: "User", receiver: "User", tip: "Union[CurrencyItem, Item]") -> None:
        try:
            if receiver.id == self.bot.bot_id:
                amount = getattr(tip, 'amount', 'unknown')
                currency = getattr(tip, 'currency', 'gold')
                await self.bot.highrise.chat(f"✨ Thank you @{sender.username} for the {amount} {currency} tip!")
        except Exception as e:
            print(f"Error in on_tip: {e}")

    


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
        
        # --- EMOTE LOOP COMMAND ---
        if trigger in EMOTE_DICT:
            actual_emote = EMOTE_DICT[trigger]
            # Use the target if mentioned, otherwise the person who sent the command
            target_name = args[0].replace("@", "").lower() if args else user.username.lower()
            
            room_users = (await self.bot.highrise.get_room_users()).content
            target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
            
            if target:
                # 1. Stop any existing loop for this specific target before starting a new one
                if target_name in self.active_tasks:
                    self.looping_users[target_name] = False
                    self.active_tasks[target_name].cancel()
                    await asyncio.sleep(0.5) 
                
                # 2. Start new loop
                self.looping_users[target_name] = True
                task = asyncio.create_task(self.loop_emote(actual_emote, target.id, target_name))
                self.active_tasks[target_name] = task
                await self.bot.highrise.chat(f"✨ Looping {trigger} for @{target_name}!")
            return

        # --- STOP COMMAND ---
        if trigger in ["stop", "0"]:
            # Stop the loop for the person who sent the command
            name_to_stop = user.username.lower()
            if name_to_stop in self.active_tasks:
                self.looping_users[name_to_stop] = False
                self.active_tasks[name_to_stop].cancel()
                await self.bot.highrise.chat(f"⏹️ Stopped your emote loop.")
            return
        
        # --- WALLET COMMAND (SUMMATION) ---
        if trigger == "/wallet" and is_owner:
            try:
                wallet = await self.bot.highrise.get_wallet()
                total_gold = 0
                
                # Iterate through all items in the wallet content
                for item in wallet.content:
                    # Check if the item is related to currency or gold
                    # We look for the 'amount' attribute in each item
                    if hasattr(item, 'amount'):
                        total_gold += item.amount
                
                await self.bot.highrise.chat(f"💰 Bot Wallet Balance: {total_gold} Gold")
            except Exception as e:
                await self.bot.highrise.chat(f"❌ Error checking wallet: {e}")
                print(f"DEBUG Error: {e}")
            return
        # --- TIP COMMAND (Single or All) ---
        if trigger == "/tip" and is_owner:
            if len(args) < 2:
                await self.bot.highrise.chat("Usage: /tip [@username/all] [1, 5, 10, 50, 100, 500, 1k, 5k, 10k]")
                return

            target_input = args[0].replace("@", "").lower()
            amount = args[1]
            # Map common inputs to Highrise gold IDs
            item_id = f"gold_bar_{amount}"
            
            # Verify the item_id is valid
            valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100", 
                         "gold_bar_500", "gold_bar_1k", "gold_bar_5000", "gold_bar_10k"]
            
            if item_id not in valid_ids:
                await self.bot.highrise.chat("❌ Invalid amount. Use: 1, 5, 10, 50, 100, 500, 1k, 5k, 10k.")
                return

            room_users = (await self.bot.highrise.get_room_users()).content

            if target_input == "all":
                await self.bot.highrise.chat(f"💎 Tipping everyone {amount} gold...")
                for user_obj, _ in room_users:
                    if user_obj.id == self.bot.bot_id: continue 
                    try:
                        await self.bot.highrise.tip_user(user_obj.id, item_id)
                        await asyncio.sleep(1) # Crucial to prevent rate limits
                    except Exception as e:
                        print(f"Failed to tip {user_obj.username}: {e}")
                await self.bot.highrise.chat("✅ Finished tipping everyone!")
            else:
                target = next((r for r, _ in room_users if r.username.lower() == target_input), None)
                if target:
                    try:
                        await self.bot.highrise.tip_user(target.id, item_id)
                        await self.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
                    except Exception as e:
                        await self.bot.highrise.chat(f"❌ Failed: {e}")
                else:
                    await self.bot.highrise.chat("❌ User not found.")
            return
        
        # --- WHISPER LIST EMOTES COMMAND ---
        if trigger == "/list":
            # Default to page 1 if no page is specified
            page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
            
            # 10 items per page
            start = (page - 1) * 10
            end = start + 10
            
            # Fetch the specific chunk from the master list
            chunk = EMOTE_DICT[start:end]
            
            # If the page is empty, tell the user
            if not chunk:
                await self.bot.highrise.send_whisper(user.id, "❌ That page does not exist.")
                return
            
            # Format the message
            msg = f"📜 Page {page} (Emotes {start} to {min(end, len(EMOTE_DICT)) - 1}):\n"
            for i, emote in enumerate(chunk, start=start):
                msg += f"{i}: {emote['name']}\n"
            
            msg += "\nUse /emote [number] to play!"
            
            # Whisper the message directly to the user
            await self.bot.highrise.send_whisper(user.id, msg)
            return