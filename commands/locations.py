from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lstrip("/").lower()
    
    # Ensure locations dictionary exists
    if "locations" not in handler.data:
        handler.data["locations"] = {}

    # 1. TELEPORT (If cmd is a saved location name)
    if cmd in handler.data["locations"]:
        loc = handler.data["locations"][cmd]
        await handler.bot.highrise.teleport(user.id, Position(loc["x"], loc["y"], loc["z"], loc["f"]))
        await handler.bot.highrise.chat(f"🚀 Teleporting to {cmd}!")
        return

    # 2. SET LOCATION
    if cmd == "set":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /set [name]")
            return
        
        name = parts[1].lower()
        room_users = await handler.bot.highrise.get_room_users()
        for u, pos in room_users.content:
            if u.id == user.id:
                handler.data["locations"][name] = {"x": pos.x, "y": pos.y, "z": pos.z, "f": pos.facing}
                handler.save_data()
                await handler.bot.highrise.chat(f"✅ Location '{name}' saved!")
                return

    # 3. LIST LOCATIONS
    elif cmd == "clocs":
        locs = list(handler.data["locations"].keys())
        if not locs:
            await handler.bot.highrise.chat("No locations saved.")
        else:
            await handler.bot.highrise.chat(f"Saved: {', '.join(locs)}")