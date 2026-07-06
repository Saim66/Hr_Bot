from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 1:
        return
    
    cmd = parts[0].lstrip("/").lower()
    
    # 1. Get room user data
    room_users = await handler.bot.highrise.get_room_users()
    
    # 2. Find Bot position and handle target user info
    bot_pos = None
    target_id = None
    target_pos = None
    
    # Find bot position
    for u, pos in room_users.content:
        if u.id == handler.bot.user_id:
            bot_pos = pos
            break

    # 3. Handle Commands
    
    # --- SUMMON (/s @user) ---
    if cmd == "s":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /s @username")
            return
        target_name = parts[1].lstrip("@").lower()
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_id = u.id
                break
        if target_id and bot_pos:
            await handler.bot.highrise.teleport(target_id, bot_pos)
            await handler.bot.highrise.chat(f"✨ Summoned @{target_name} to me!")
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_name} not found.")

    # --- TELEPORT (/to @user) ---
    elif cmd == "to":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /to @username")
            return
        target_name = parts[1].lstrip("@").lower()
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_pos = pos
                break
        if target_pos:
            await handler.bot.highrise.teleport(handler.bot.user_id, target_pos)
            await handler.bot.highrise.chat(f"🚀 Teleporting to @{target_name}!")
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_name} not found.")

    # --- CORDS (/cords) ---
    elif cmd == "cords":
        for u, pos in room_users.content:
            if u.id == user.id:
                await handler.bot.highrise.chat(
                    f"@{user.username}: {pos.x}, {pos.y}, {pos.z} | Facing: {pos.facing}"
                )
                break
