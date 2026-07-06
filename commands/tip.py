async def execute(handler, user, message):
    parts = message.split()
    
    # Usage: /tip @username amount
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip @username [amount]")
        return
    
    target_username = parts[1].lstrip("@").lower()
    amount = parts[2]
    
    # Find the target user in the room
    room_users = await handler.bot.highrise.get_room_users()
    target_user = None
    for u, pos in room_users.content:
        if u.username.lower() == target_username:
            target_user = u
            break
            
    if not target_user:
        await handler.bot.highrise.chat("User not found in this room.")
        return

    try:
        # Note: You must use valid Highrise currency IDs
        # Most bots use 'gold_bar_1' for 1 gold
        await handler.bot.highrise.tip_user(target_user.id, "gold_bar_1")
        await handler.bot.highrise.chat(f"Tipped @{target_user.username}!")
    except Exception as e:
        print(f"Tip error: {e}")
        await handler.bot.highrise.chat("❌ Failed to tip. Ensure the bot has enough gold and permissions.")