async def execute(handler, user, message):
    # If the message is exactly "join_event", run the welcome logic
    if message == "join_event":
        try:
            # Check if user is VIP
            is_vip = user.username.lower() in [v.lower() for v in handler.data.get("vips", [])]
            
            if is_vip:
                await handler.bot.highrise.chat(f"👑 Welcome back, VIP @{user.username}!")
            else:
                await handler.bot.highrise.chat(f"👋 Hello @{user.username}, welcome to the room!")
            return # Exit after finishing join event
        except Exception as e:
            print(f"Error in welcome trigger: {e}")
            return

    # Otherwise, handle as manual command
    parts = message.split()
    cmd = parts[0].lstrip("/").lower()
    if cmd == "welcome":
        await handler.bot.highrise.chat("✅ Welcome system is active!")
