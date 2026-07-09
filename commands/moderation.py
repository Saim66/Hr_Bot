import asyncio
import config # Import the config file

async def execute(handler, user, message):
    # Permission Gate: Check if user is Owner or Moderator
    if not config.is_staff(user.username):
        await handler.bot.highrise.chat(f"🚫 @{user.username}, this is a Staff-only command.")
        return

    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /kick @username or /ban @username")
        return
    
    cmd = parts[0].lstrip("/").lower()
    target_name = parts[1].lstrip("@").lower()
    
    # Get the list of users to find the ID
    room_users = await handler.bot.highrise.get_room_users()
    target_id = None
    for u, pos in room_users.content:
        if u.username.lower() == target_name:
            target_id = u.id
            break
            
    if not target_id:
        await handler.bot.highrise.chat(f"❌ User @{target_name} not found in room.")
        return

    # Perform the moderation
    try:
        if cmd == "kick":
            await handler.bot.highrise.moderate_room(target_id, "kick")
            await handler.bot.highrise.chat(f"👢 @{target_name} has been kicked.")
        elif cmd == "ban":
            # 3600 seconds = 1 hour ban
            await handler.bot.highrise.moderate_room(target_id, "ban", 3600)
            await handler.bot.highrise.chat(f"🚫 @{target_name} has been banned for 1 hour.")
        elif cmd == "unban":
            await handler.bot.highrise.moderate_room(target_id, "unban")
            await handler.bot.highrise.chat(f"✅ @{target_name} has been unbanned.")
    except Exception as e:
        await handler.bot.highrise.chat(f"❌ Error: {e}")
