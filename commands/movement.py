from highrise import User, Position # This is correct

async def execute(handler, user: User, message: str):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /s @username")
        return
    
    cmd = parts[0].lstrip("/").lower()
    target_username = parts[1].lstrip("@").lower()
    
    # 1. Fetch room users
    room_users = await handler.bot.highrise.get_room_users()
    
    target_id = None
    bot_pos = None
    
    # 2. Identify the target and the bot's own position
    for u, pos in room_users.content:
        # Find target
        if u.username.lower() == target_username:
            target_id = u.id
        # Find bot (using the bot's user_id we initialized in main.py)
        if u.id == handler.bot.user_id:
            bot_pos = pos
            
    # 3. Execution logic for Summon
    if cmd == "s":
        if not target_id:
            await handler.bot.highrise.chat(f"❌ User @{target_username} not found.")
            return
        if not bot_pos:
            await handler.bot.highrise.chat("❌ Could not determine my own position.")
            return
            
        try:
            await handler.bot.highrise.teleport(target_id, bot_pos)
            await handler.bot.highrise.chat(f"✨ Summoned @{target_username} to my location!")
        except Exception as e:
            print(f"Summon error: {e}")
            await handler.bot.highrise.chat("❌ Failed to summon. Do I have Host/Mod permissions?")

    # 2. TO: Move BOT to target user's position
    elif cmd == "to":
        target_name = parts[1].lstrip("@").lower()
        room_users = await handler.bot.highrise.get_room_users()
        
        target_pos = None
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_pos = pos
                break
        
        if target_pos:
            # Instead of relying on user_id, use the bot's direct interaction
            await handler.bot.highrise.teleport(handler.bot.user_id, target_pos)
            await handler.bot.highrise.chat(f"🚀 Teleporting to @{target_name}!")

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