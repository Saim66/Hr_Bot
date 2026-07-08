from highrise import Position

async def execute(handler, user, message):
    parts = message.strip().split()
    if not parts:
        return
        
    raw_cmd = parts[0].lower() # e.g., "/set" or "f1"
    
    # 1. HANDLE SLASH COMMANDS (/set, /dloc, /clocs)
    if raw_cmd.startswith("/"):
        trigger = raw_cmd.lstrip("/")
        
        if trigger == "set":
            if len(parts) < 2: 
                await handler.bot.highrise.chat("Usage: /set [name]")
                return
            loc_name = parts[1].lower()
            room_users = await handler.bot.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.id == user.id:
                    handler.locations[loc_name] = {
                        "x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing
                    }
                    handler.save_locations()
                    await handler.bot.highrise.chat(f"📍 Location '{loc_name}' saved!")
                    return

        elif trigger == "dloc":
            if len(parts) < 2: return
            loc_name = parts[1].lower()
            if loc_name in handler.locations:
                del handler.locations[loc_name]
                handler.save_locations()
                await handler.bot.highrise.chat(f"🗑️ Deleted '{loc_name}'.")
            else:
                await handler.bot.highrise.chat(f"❌ '{loc_name}' not found.")
        
        elif trigger == "clocs":
            if not handler.locations:
                await handler.bot.highrise.chat("📍 No locations saved.")
                return
            locs = ", ".join(handler.locations.keys())
            await handler.bot.highrise.chat(f"📍 Locations: {locs}")

    # 2. HANDLE TELEPORT WITHOUT PREFIX (f1, f2, etc.)
    elif raw_cmd in handler.locations:
        data = handler.locations[raw_cmd]
        try:
            target_pos = Position(data['x'], data['y'], data['z'], data['facing'])
            await handler.bot.highrise.teleport(user.id, target_pos)
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Teleport error: {e}")
