async def execute(handler, user, message):
    # This checks if it's a manual command ("/welcome") or an internal trigger
    parts = message.split()
    cmd = parts[0].lstrip("/").lower()
    
    # Logic for manual "/welcome" command
    if cmd == "welcome":
        await handler.bot.highrise.chat("✅ Welcome system is active!")
        return

    # Logic for automatic join event (triggered by main.py)
    # The message is passed as "join_event" from the trigger below
    if message == "join_event":
        try:
            # Check if user is VIP
            is_vip = user.username.lower() in [v.lower() for v in handler.data.get("vips", [])]
            
            if is_vip:
                await handler.bot.highrise.chat(f"👑 Welcome back, VIP @{user.username}!")
            else:
                await handler.bot.highrise.chat(f"👋 Hello @{user.username}, welcome to the room!")
        except Exception as e:
            print(f"Error in welcome trigger: {e}")