import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2: return
    
    cmd = parts[0].lstrip("/").lower()
    target_name = parts[1].lstrip("@").lower()
    
    room_users = await handler.bot.highrise.get_room_users()
    target_id = None
    for u, pos in room_users.content:
        if u.username.lower() == target_name:
            target_id = u.id
            break
            
    if not target_id:
        await handler.bot.highrise.chat("User not found.")
        return

    # Use handler.bot.user_id to check if bot is trying to ban itself
    if cmd == "kick":
        await handler.bot.highrise.kick_user(target_id)
    elif cmd == "ban":
        await handler.bot.highrise.ban_user(target_id)
    elif cmd == "unban":
        await handler.bot.highrise.unban_user(target_id)
      