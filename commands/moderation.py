import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /kick @username or /ban @username")
        return
    
    cmd = parts[0].lstrip("/").lower()
    target_name = parts[1].lstrip("@").lower()
    
    # 1. Get the list of users to find the ID
    room_users = await handler.bot.highrise.get_room_users()
    target_id = None
    for u, pos in room_users.content:
        if u.username.lower() == target_name:
            target_id = u.id
            break
            
    if not target_id:
        await handler.bot.highrise.chat(f"User {target_name} not found.")
        return

    # 2. Perform the moderation
    try:
        if cmd == "kick":
            await handler.bot.highrise.moderate_room(target_id, "kick")
            await handler.bot.highrise.chat(f"Kicked {target_name}")
        elif cmd == "ban":
            # 3600 seconds = 1 hour ban
            await handler.bot.highrise.moderate_room(target_id, "ban", 3600)
            await handler.bot.highrise.chat(f"Banned {target_name}")
        elif cmd == "unban":
            await handler.bot.highrise.moderate_room(target_id, "unban")
            await handler.bot.highrise.chat(f"Unbanned {target_name}")
    except Exception as e:
        await handler.bot.highrise.chat(f"Error: {e}")
