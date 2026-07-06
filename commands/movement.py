from highrise import Position, User

async def execute(handler, user: User, message: str):
    parts = message.split()
    if not parts:
        return
    
    cmd = parts[0].lstrip("/").lower()
    
    # 1. SUMMON: Move target user to BOT's current position
    if cmd == "s":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /s @username")
            return
            
        target_name = parts[1].lstrip("@").lower()
        room_users = await handler.bot.highrise.get_room_users()
        
        target_id = None
        bot_pos = None
        
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_id = u.id
            if u.id == handler.bot.user_id:
                bot_pos = pos
                
        if target_id and bot_pos:
            await handler.bot.highrise.teleport(target_id, bot_pos)
            await handler.bot.highrise.chat(f"✨ Summoned @{target_name} to me!")
        else:
            await handler.bot.highrise.chat("❌ Target not found or bot position unknown.")

    # 2. TO: Move BOT to target user's position
    elif cmd == "to":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /to @username")
            return
            
        target_name = parts[1].lstrip("@").lower()
        room_users = await handler.bot.highrise.get_room_users()
        
        target_pos = None
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_pos = pos
                break
                
        if target_pos:
            await handler.bot.highrise.teleport(handler.bot.user_id, target_pos)
            await handler.bot.highrise.chat(f"🚀 Teleporting to @{target_name}!")
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_name} not found.")

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