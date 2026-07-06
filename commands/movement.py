from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        return
    
    cmd = parts[0].lstrip("/").lower()
    target_username = parts[1].lstrip("@").lower()
    
    # 1. Fetch everyone in the room
    room_users = await handler.bot.highrise.get_room_users()
    
    target_id = None
    target_pos = None
    bot_pos = None
    
    # 2. Find target's data and Bot's position
    for u, pos in room_users.content:
        if u.username.lower() == target_username:
            target_id = u.id
            target_pos = pos
        if u.id == handler.bot.user_id:
            bot_pos = pos
            
    if not target_id:
        await handler.bot.highrise.chat(f"@{target_username} not found.")
        return

    # 3. COMMAND LOGIC
    # /s @user -> Teleport TARGET to BOT
    if cmd == "s":
        if bot_pos:
            await handler.bot.highrise.teleport(target_id, bot_pos)
            await handler.bot.highrise.chat(f"✨ Summoned @{target_username}!")
            
    # /to @user -> Teleport BOT to TARGET
    elif cmd == "to":
        if target_pos:
            await handler.bot.highrise.teleport(handler.bot.user_id, target_pos)
            await handler.bot.highrise.chat(f"🚀 Teleporting to @{target_username}!")
)


    # 3. CORDS: Get your own current coordinates
    elif cmd == "cords":
        room_users = await handler.bot.highrise.get_room_users()
        found = False
        for u, pos in room_users.content:
            if u.id == user.id:
                await handler.bot.highrise.chat(
                    f"@{user.username}: {pos.x}, {pos.y}, {pos.z} | Facing: {pos.facing}"
                )
                found = True
                break
        if not found:
            await handler.bot.highrise.chat("❌ Could not find your coordinates.")