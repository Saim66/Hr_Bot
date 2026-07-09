from highrise import Position
import config
import json
import os

# Path to your VIP data on the Railway volume
VIP_DATA_PATH = "/var/lib/containers/railwayapp/bind-mounts/vol_iatnm6uo2p12iuk5/vips.json"

def get_authorized_users():
    """Loads VIP list from the persistent volume."""
    try:
        if os.path.exists(VIP_DATA_PATH):
            with open(VIP_DATA_PATH, 'r') as f:
                data = json.load(f)
                return [user.lower() for user in data.get("vips", [])]
        return []
    except Exception as e:
        print(f"Error loading VIPs: {e}")
        return []

async def execute(handler, user, message):
    parts = message.strip().split()
    if not parts:
        return
        
    raw_cmd = parts[0].lower()
    
    # 1. OWNER-ONLY ADMIN COMMANDS (/set, /dloc, /clocs)
    if raw_cmd.startswith("/"):
        if not config.is_owner(user.username):
            await handler.bot.highrise.chat(f"🚫 @{user.username}, this is an Owner-only command.")
            return

        trigger = raw_cmd.lstrip("/")
        
        if trigger == "set":
            if len(parts) < 2: 
                await handler.bot.highrise.chat("Usage: /set [location_name]")
                return
            
            loc_name = parts[1].lower()
            room_users = await handler.bot.highrise.get_room_users()
            target_pos = next((pos for u, pos in room_users.content if u.id == user.id), None)
            
            if target_pos:
                handler.locations[loc_name] = {
                    "x": target_pos.x, "y": target_pos.y, "z": target_pos.z, "facing": target_pos.facing
                }
                handler.save_locations()
                await handler.bot.highrise.chat(f"📍 Location '{loc_name}' saved!")
            
        elif trigger == "dloc":
            loc_name = parts[1].lower() if len(parts) > 1 else ""
            if loc_name in handler.locations:
                del handler.locations[loc_name]
                handler.save_locations()
                await handler.bot.highrise.chat(f"🗑️ Location '{loc_name}' deleted.")
            else:
                await handler.bot.highrise.chat(f"❌ Location '{loc_name}' not found.")
        
        elif trigger == "clocs":
            locs = ", ".join(handler.locations.keys()) if handler.locations else "None"
            await handler.bot.highrise.chat(f"📍 Saved locations: {locs}")

    # 2. RESTRICTED TELEPORT (Owner, Admin, or VIP from Volume)
    elif raw_cmd in handler.locations:
        authorized_users = get_authorized_users()
        
        # Permission check: Owner OR in the VIP file
        if not (config.is_owner(user.username) or user.username.lower() in authorized_users):
            await handler.bot.highrise.chat(f"💎 @{user.username}, you need VIP access to use this.")
            return

        data = handler.locations[raw_cmd]
        target_pos = Position(data['x'], data['y'], data['z'], data['facing'])
        await handler.bot.highrise.teleport(user.id, target_pos)
