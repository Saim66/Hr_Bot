# commands/moderation.py

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    trigger = parts[0]
    args = parts[1:]
    is_owner = user.username.lower() == handler.bot.config.OWNER_USERNAME.lower()

    if trigger == "/welcome" and is_owner and len(args) >= 2:
        target = args[0].replace("@", "").lower()
        handler.data["welcomes"][target] = " ".join(args[1:])
        handler.save_data()
        await handler.bot.highrise.chat(f"✅ Welcome set for @{target}")

    elif trigger in ["/kick", "/ban"] and is_owner and args:
        target_name = args[0].replace("@", "").lower()
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        if target:
            await handler.bot.highrise.moderate_room(target.id, trigger.replace("/", ""))
            await handler.bot.highrise.chat(f"🚫 @{target.username} has been {trigger.replace('/', '')}ed.")