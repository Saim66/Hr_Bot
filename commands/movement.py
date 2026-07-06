from highrise import User, Position # This is correct


async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        return
    
    cmd = parts[0].lstrip("/").lower()
    target_name = parts[1].lstrip("@").lower()
    
    # Fetch room users
    room_users = await handler.bot.highrise.get_room_users()
    target_id = None
    target_pos = None
    
    for u, pos in room_users.content:
        if u.username.lower() == target_name:
            target_id = u.id
            target_pos = pos
            break
            
    # Use the bot's known ID
    bot_id = handler.bot.user_id 
    bot_pos = None
    for u, pos in room_users.content:
        if u.id == bot_id:
            bot_pos = pos
            break

    # COMMAND: Summon (/s)
    if cmd == "s" and target_id and bot_pos:
        await handler.bot.highrise.teleport(target_id, bot_pos)
        
    # COMMAND: Teleport to user (/to)
    elif cmd == "to" and target_pos:
        await handler.bot.highrise.teleport(bot_id, target_pos)


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