async def execute(handler, user, message):
    print(f"DEBUG: Locations command received: {message}")
    parts = message.split()
    command = parts[0].lstrip("/")
    
    # 1. SET LOCATION
    if command == "set":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /set [loc_name]")
            return
        loc_name = parts[1]
        # Assuming you have a bot.get_user_position() or similar
        # For Highrise, you usually need to get the user's position from the room users list
        users = await handler.bot.highrise.get_room_users()
        for u, pos in users.content:
            if u.id == user.id:
                handler.locations[loc_name] = {"x": pos.x, "y": pos.y, "z": pos.z, "f": pos.facing}
                handler.save_locations()
                await handler.bot.highrise.chat(f"Location '{loc_name}' saved!")
                return

    # 2. DELETE LOCATION
    elif command == "dloc":
        if len(parts) < 2: return
        if parts[1] in handler.locations:
            del handler.locations[parts[1]]
            handler.save_locations()
            await handler.bot.highrise.chat(f"Location '{parts[1]}' deleted.")

    # 3. LIST LOCATIONS
    elif command == "clocs":
        loc_list = ", ".join(handler.locations.keys())
        await handler.bot.highrise.chat(f"Locations: {loc_list}")