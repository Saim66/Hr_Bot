import asyncio

async def execute(handler, user, message):
    parts = message.split()
    command = parts[0].lstrip("/").lower()
    
    # Check if a target username was provided
    if len(parts) < 2:
        await handler.bot.highrise.chat(f"⚠️ Usage: /{command} [@username]")
        return
        
    # Clean the target name (remove @ and make lowercase)
    target_username = parts[1].lstrip("@").lower()
    
    # Fetch all users in the room to find the target's user ID
    room_users = await handler.bot.highrise.get_room_users()
    target_user = None
    
    for r_user, position in room_users.content:
        if r_user.username.lower() == target_username:
            target_user = r_user
            break
            
    if not target_user:
        await handler.bot.highrise.chat(f"❌ User @{parts[1].lstrip('@')} not found in this room.")
        return

    # Don't let the bot moderation commands apply to the bot itself
    if target_user.id == handler.bot.id:
        await handler.bot.highrise.chat("🤖 You cannot kick or ban the bot!")
        return

    # 1. KICK COMMAND
    if command == "kick":
        try:
            await handler.bot.highrise.kick_user(target_user.id)
            await handler.bot.highrise.chat(f"🚪 @{target_user.username} has been kicked from the room.")
        except Exception as e:
            print(f"Error kicking user: {e}")
            await handler.bot.highrise.chat("❌ Failed to kick user. Make sure the bot has Host/Mod privileges.")

    # 2. BAN COMMAND
    elif command == "ban":
        try:
            # Highrise ban expects: user_id and duration (seconds). 86400 seconds = 1 day
            # If your SDK version doesn't use duration, it defaults to permanent or uses just user_id
            try:
                await handler.bot.highrise.ban_user(target_user.id, 86400)
            except TypeError:
                # Fallback if your specific Highrise SDK method only takes user_id
                await handler.bot.highrise.ban_user(target_user.id)
                
            await handler.bot.highrise.chat(f"🚫 @{target_user.username} has been banned.")
        except Exception as e:
            print(f"Error banning user: {e}")
            await handler.bot.highrise.chat("❌ Failed to ban user. Make sure the bot has Host privileges.")

    # 3. UNBAN COMMAND
    elif command == "unban":
        if len(parts) < 2:
            await handler.bot.highrise.chat("⚠️ Usage: /unban [user_id]")
            return
        
        target_id = parts[1]
        try:
            await handler.bot.highrise.unban_user(target_id)
            await handler.bot.highrise.chat(f"✅ User with ID {target_id} has been unbanned.")
        except Exception as e:
            print(f"Error unbanning: {e}")
            await handler.bot.highrise.chat("❌ Failed to unban. Ensure the ID is correct.")        