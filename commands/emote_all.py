import asyncio

async def execute(handler, user, message):
    # 1. Parse arguments
    args = message.split()[1:]
    if not args:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = args[0]
    
    # 2. Get all users in the room
    try:
        room_users = await handler.bot.highrise.get_room_users()
    except Exception as e:
        print(f"Failed to fetch room users: {e}")
        return

    # 3. Iterate and send emote
    # We use a task group or sequential await with delay to avoid rate limits
    sent_count = 0
    for room_user, _ in room_users.content:
        try:
            # Skip the bot itself
            if room_user.id == handler.bot.bot_id:
                continue
                
            await handler.bot.highrise.send_emote(emote_name, room_user.id)
            sent_count += 1
            # Small delay to respect API rate limits and prevent crashing
            await asyncio.sleep(0.5) 
        except Exception as e:
            # This skips users who are restricted or cannot emote
            continue 

    if sent_count > 0:
        await handler.bot.highrise.chat(f"✨ Emote '{emote_name}' sent to {sent_count} users!")
    else:
        await handler.bot.highrise.chat(f"⚠️ Could not send '{emote_name}' to any users.")