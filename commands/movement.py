from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    if not parts:
        await handler.bot.highrise.chat("Usage: /s @username OR /to @username OR /cords")
        return

    cmd = parts[0].lstrip("/").lower()

    if cmd == "cords":
        room_users = await handler.bot.highrise.get_room_users()
        for u, pos in room_users.content:
            if u.id == user.id:
                await handler.bot.highrise.chat(f"@{user.username}: {pos.x}, {pos.y}, {pos.z} - {pos.facing}")
                return
        await handler.bot.highrise.chat("Could not find your coordinates.")
        return

    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /s @username OR /to @username OR /cords")
        return
    
    target_username = parts[1].lstrip("@").lower()
    
    # 1. Get all users in the room
    room_users = await handler.bot.highrise.get_room_users()
    
    # 2. Find the target user and the bot's own position
    target_user_id = None
    target_pos = None
    bot_pos = None
    
    for u, pos in room_users.content:
        # Find the target
        if u.username.lower() == target_username:
            target_user_id = u.id
            target_pos = pos
        # Find the bot
        if u.id == handler.bot.user_id:
            bot_pos = pos
            
    if not target_user_id:
        await handler.bot.highrise.chat(f"User @{target_username} not found in room.")
        return

    # 3. Execute movement
    try:
        if cmd == "s": # Summon: move target to BOT's position
            if not bot_pos:
                await handler.bot.highrise.chat("Could not find bot position.")
                return
            await handler.bot.highrise.teleport(target_user_id, bot_pos)
            await handler.bot.highrise.chat(f"Summoned @{target_username} to me!")
            
        elif cmd == "to": # Teleport: move BOT to TARGET's position
            await handler.bot.highrise.teleport(user.id, target_pos) # user.id refers to the person who triggered command
            await handler.bot.highrise.chat(f"Teleporting to @{target_username}!")
            
    except Exception as e:
        print(f"Movement error: {e}")
        await handler.bot.highrise.chat("❌ Failed to move. I need Moderator/Host permissions!")