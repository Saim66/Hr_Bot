async def execute(handler, user, message):
    args = message.split()[1:]
    is_owner = user.username.lower() == handler.bot.config.OWNER_USERNAME.lower()

    if not is_owner:
        return

    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /welcome @username [message]")
        return

    # Extract target username and the welcome message
    target = args[0].replace("@", "").lower()
    welcome_msg = " ".join(args[1:])

    # Store in your data structure
    handler.data["welcomes"][target] = welcome_msg
    handler.save_data()
    
    await handler.bot.highrise.chat(f"✅ Welcome message set for @{target}")