async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /vip [add/remove] [@username]")
        return

    action = parts[1].lower()
    target_name = parts[2].lstrip("@").lower()

    if action == "add":
        if target_name not in handler.data.get("vips", []):
            handler.data.setdefault("vips", []).append(target_name)
            handler.save_data() # Ensure this method exists in your handler
            await handler.bot.highrise.chat(f"✅ @{target_name} added to VIP list.")
        else:
            await handler.bot.highrise.chat(f"@{target_name} is already a VIP.")

    elif action == "remove":
        if target_name in handler.data.get("vips", []):
            handler.data["vips"].remove(target_name)
            handler.save_data()
            await handler.bot.highrise.chat(f"✅ @{target_name} removed from VIP list.")
        else:
            await handler.bot.highrise.chat(f"@{target_name} is not in the VIP list.")