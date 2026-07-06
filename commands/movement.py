# commands/movement.py
from highrise import Position

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    trigger = parts[0]
    args = parts[1:]
    
    is_owner = user.username.lower() == handler.bot.config.OWNER_USERNAME.lower()
    is_vip = user.username.lower() in handler.data.get("vips", []) or is_owner

    if trigger in ["/s", "/to"] and is_vip:
        if not args: return
        target_name = args[0].replace("@", "").lower()
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        
        if target:
            if trigger == "/s":
                my_pos = next((p for r, p in room_users if r.id == user.id), None)
                if my_pos: await handler.bot.highrise.teleport(target.id, my_pos)
            else:
                t_pos = next((p for r, p in room_users if r.id == target.id), None)
                if t_pos: await handler.bot.highrise.teleport(user.id, t_pos)
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_name} not found.")

    elif trigger == "/cords":
        room_users = await handler.bot.highrise.get_room_users()
        for room_user, position in room_users.content:
            if room_user.id == user.id:
                coords = f"📍 Your Coordinates: X={position.x}, Y={position.y}, Z={position.z}"
                await handler.bot.highrise.send_whisper(user.id, coords)
                return