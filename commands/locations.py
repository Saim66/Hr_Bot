from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower() # This will be the name (e.g., "stage") or command (e.g., "/set")

    # 1. HANDLE COMMANDS WITH SLASH
    if cmd.startswith("/"):
        trigger = cmd.lstrip("/")
        
        if trigger == "set":
            if len(parts) < 2: return
            loc_name = parts[1].lower()
            room_users = await handler.bot.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.id == user.id:
                    handler.locations[loc_name] = {"x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing}
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
        
        elif trigger == "clocs":
            locs = ", ".join(handler.locations.keys())
            await handler.bot.highrise.chat(f"📍 Locations: {locs}")

    # 2. HANDLE TELEPORT WITHOUT PREFIX (The Location Name itself)
    elif cmd in handler.locations:
        data = handler.locations[cmd]
        try:
            target_pos = Position(data['x'], data['y'], data['z'], data['facing'])
            await handler.bot.highrise.teleport(user.id, target_pos)
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Teleport error: {e}")
