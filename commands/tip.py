import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    # Check for minimal arguments
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [@username/all] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    item_id = f"gold_bar_{amount}"

    # Validate Gold Amount
    valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", 
                 "gold_bar_100", "gold_bar_500", "gold_bar_5000", "gold_bar_10000"]
    
    if item_id not in valid_ids:
        await handler.bot.highrise.chat("❌ Invalid amount. Use 1, 5, 10, 50, 100, 500, 5000, or 10000.")
        return

    # Fetch room users
    room_users = (await handler.bot.highrise.get_room_users()).content

    # Logic for /tip all [amount]
    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        for user_obj, _ in room_users:
            # Skip the sender and the bot itself (assuming your bot's SDK uses user.id)
            if user_obj.id == user.id:
                continue
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                await asyncio.sleep(1.2) # Delay to prevent rate limiting
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        await handler.bot.highrise.chat("✅ Finished tipping everyone.")

    # Logic for /tip @username [amount]
    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        if target:
            try:
                await handler.bot.highrise.tip_user(target.id, item_id)
                await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed to tip: {e}")
        else:
            await handler.bot.highrise.chat("❌ User not found in this room.")
