# commands/locations.py
from highrise import Position

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    trigger = parts[0]
    args = parts[1:]
    is_owner = user.username.lower() == handler.bot.config.OWNER_USERNAME.lower()

    # Teleport to saved location
    if trigger in handler.locations:
        if trigger in handler.data.get("restricted", []) and not is_owner:
            await handler.bot.highrise.chat(f"🚫 Sorry @{user.username}, that is an Owner-only area!")
            return
        loc = handler.locations[trigger]
        target_pos = Position(float(loc['x']), float(loc['y']), float(loc['z']), loc['facing'])
        await handler.bot.highrise.teleport(user.id, target_pos)
        await handler.bot.highrise.chat(f"🚀 Teleporting to {trigger}!")

    # Manage locations
    elif trigger == "/set" and is_owner and args:
        loc_name = args[0].lower()
        room_users = (await handler.bot.highrise.get_room_users()).content
        my_pos = next((p for r, p in room_users if r.id == user.id), None)
        if my_pos:
            handler.locations[loc_name] = {"x": my_pos.x, "y": my_pos.y, "z": my_pos.z, "facing": my_pos.facing}
            handler.save_locations()
            await handler.bot.highrise.chat(f"✅ Location '{loc_name}' saved!")

    elif trigger in ["/dloc", "/deleteloc"] and is_owner and args:
        if args[0].lower() in handler.locations:
            del handler.locations[args[0].lower()]
            handler.save_locations()
            await handler.bot.highrise.chat(f"🗑️ Deleted '{args[0]}'.")

    elif trigger == "/clocs" and is_owner:
        loc_list = ", ".join(handler.locations.keys())
        await handler.bot.highrise.chat(f"📂 Saved locations: {loc_list if loc_list else 'None'}")