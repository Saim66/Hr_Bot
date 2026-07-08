from highrise import Position

async def execute(handler, user, message):
    """
    Handles both admin commands (/set, /dloc, /clocs) 
    and direct teleportation (f1, f2, etc.)
    """
    parts = message.strip().split()
    if not parts:
        return
        
    # Get the raw command (e.g., "/set" or "f1")
    raw_cmd = parts[0].lower()
    
    # 1. HANDLE SLASH COMMANDS (/set, /dloc, /clocs)
    if raw_cmd.startswith("/"):
        trigger = raw_cmd.lstrip("/")
        
        if trigger == "set":
            if len(parts) < 2: 
                await handler.bot.highrise.chat("Usage: /set [location_name]")
                return
            
            loc_name = parts[1].lower()
            room_users = await handler.bot.highrise.get_room_users()
            
            # Find the user's position
            target_pos = None
            for u, pos in room_users.content:
                if u.id == user.id:
                    target_pos = pos
                    break
            
            if target_pos:
                handler.locations[loc_name] = {
                    "x": target_pos.x, 
                    "y": target_pos.y, 
                    "z": target_pos.z, 
                    "facing": target_pos.facing
                }
                handler.save_locations()
                await handler.bot.highrise.chat(f"📍 Location '{loc_name}' saved at current position!")
            else:
                await handler.bot.highrise.chat("❌ Could not find your position.")

        elif trigger == "dloc":
            if len(parts) < 2: 
                await handler.bot.highrise.chat("Usage: /dloc [location_name]")
                return
            
            loc_name = parts[1].lower()
            if loc_name in handler.locations:
                del handler.locations[loc_name]
                handler.save_locations()
                await handler.bot.highrise.chat(f"🗑️ Location '{loc_name}' deleted.")
            else:
                await handler.bot.highrise.chat(f"❌ Location '{loc_name}' not found.")
        
        elif trigger == "clocs":
            if not handler.locations:
                await handler.bot.highrise.chat("📍 No locations are currently saved.")
            else:
                locs = ", ".join(handler.locations.keys())
                await handler.bot.highrise.chat(f"📍 Saved locations: {locs}")

    # 2. HANDLE TELEPORT WITHOUT PREFIX (e.g., "f1", "f2")
    # This matches the routing logic we set up in bot_commands.py
    elif raw_cmd in handler.locations:
        data = handler.locations[raw_cmd]
        try:
            target_pos = Position(data['x'], data['y'], data['z'], data['facing'])
            await handler.bot.highrise.teleport(user.id, target_pos)
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Teleport error: {e}")
