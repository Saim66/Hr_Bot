from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 1:
        return
    
    cmd = parts[0].lstrip("/").lower()
    
    # Get all users in the room
    room_users = await handler.bot.highrise.get_room_users()
    
    # 1. SUMMON: Teleport TARGET to USER (who typed the command)
    if cmd == "s":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /s @username")
            return
        
        target_name = parts[1].lstrip("@").lower()
        user_pos = None
        target_id = None
        
        # Find the position of the person who typed the command
        for u, pos in room_users.content:
            if u.id == user.id:
                user_pos = pos
            if u.username.lower() == target_name:
                target_id = u.id
        
        if target_id and user_pos:
            await handler.bot.highrise.teleport(target_id, user_pos)
            await handler.bot.highrise.chat(f"✨ Teleported @{target_name} to you!")
        else:
            await handler.bot.highrise.chat("❌ Could not find you or the target user.")

    # 2. TELEPORT: Teleport USER (who typed) to TARGET
    elif cmd == "to":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /to @username")
            return
            
        target_name = parts[1].lstrip("@").lower()
        target_pos = None
        
        # Find the target's position
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_pos = pos
                break
        
        if target_pos:
            await handler.bot.highrise.teleport(user.id, target_pos)
            await handler.bot.highrise.chat(f"🚀 Teleporting you to @{target_name}!")
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_name} not found.")

    # 3. CORDS: Get your own coordinates
    elif cmd == "cords":
        for u, pos in room_users.content:
            if u.id == user.id:
                await handler.bot.highrise.chat(
                    f"@{user.username}: {pos.x}, {pos.y}, {pos.z} | Facing: {pos.facing}"
                )
                break
