import asyncio

async def execute(handler, user, message):
    # 1. Permission Gatekeeper: Only let the owner pass
    # Replace with your actual username
    owner_username = "saim06"
    
    if user.username.lower() != owner_username.lower():
        await handler.bot.highrise.chat(f"🚫 @{user.username}, you are not the owner.")
        return

    parts = message.split()
    cmd = parts[0].lstrip("/").lower()

    # 2. Command Router for Owner
    if cmd == "restart":
        await handler.bot.highrise.chat("🔄 Restarting bot...")
        # You can trigger a full process restart if your hosting supports it
        # Otherwise, just a simple logout
        await handler.bot.highrise.logout()

    elif cmd == "shout":
        msg = " ".join(parts[1:])
        await handler.bot.highrise.chat(f"📢 **{msg}**")

    elif cmd == "emoteall":
        # Force everyone in the room to do an emote
        emote_name = parts[1] if len(parts) > 1 else "idle-dance-casual"
        room_users = (await handler.bot.highrise.get_room_users()).content
        for u, _ in room_users:
            await handler.bot.highrise.send_emote(emote_name, u.id)
