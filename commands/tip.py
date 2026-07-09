import asyncio

async def execute(handler, user, message):
    args = message.split()[1:]
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tip [@username/all] [1, 5, 10, ...]")
        return

    target_input = args[0].replace("@", "").lower()
    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # Standard Highrise API IDs
    valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100",
                 "gold_bar_500", "gold_bar_1000", "gold_bar_5000", "gold_bar_10000"]
    
    if item_id not in valid_ids:
        await handler.bot.highrise.chat("❌ Invalid amount. Use 1, 5, 10, 50, 100, 500, 1000, 5000, or 10000.")
        return

    # Get room users
    response = await handler.bot.highrise.get_room_users()
    room_users = response.content

    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        for user_obj, _ in room_users:
            # We filter out the sender to prevent self-tip errors
            if user_obj.id == user.id: 
                continue
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                await asyncio.sleep(1.2) # Essential delay to prevent rate limits
            except Exception as e: 
                print(f"Failed to tip {user_obj.username}: {e}")
        await handler.bot.highrise.chat("✅ Done tipping everyone!")
        
    else:
        # Find the specific target
        target = next((r for r, _ in room_users if r.username.lower() == target_input), None)
        if target:
            try:
                await handler.bot.highrise.tip_user(target.id, item_id)
                await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
            except Exception as e: 
                await handler.bot.highrise.chat(f"❌ Failed: {e}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
