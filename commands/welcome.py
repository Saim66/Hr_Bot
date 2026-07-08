import json

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    
    # 1. COMMAND: SET CUSTOM WELCOME (e.g., "/setwelcome Thanks for joining!")
    if parts[0].lstrip("/").lower() == "setwelcome":
        custom_msg = " ".join(parts[1:])
        handler.data["custom_welcome"] = custom_msg
        handler.save_data()
        await handler.bot.highrise.chat(f"✅ Custom welcome message saved: {custom_msg}")
        return

    # 2. TRIGGER: join_event (Public/Whisper welcome)
    if message.strip() == "join_event":
        # Check VIP status
        vips = [v.lower() for v in handler.data.get("vips", [])]
        is_vip = user.username.lower() in vips
        
        # Normal Greeting (Public chat)
        prefix = "👑 VIP" if is_vip else "👋 Hello"
        await handler.bot.highrise.chat(f"{prefix} @{user.username}, welcome to the room!")
        
        # Custom Greeting (Whisper)
        custom = handler.data.get("custom_welcome")
        if custom:
            await handler.bot.highrise.send_whisper(user.id, f"📜 Note: {custom}")
        return

    # 3. COMMAND: Check status
    if parts[0].lstrip("/").lower() == "welcome":
        await handler.bot.highrise.chat("✅ Welcome system is active!")
