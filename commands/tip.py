import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    # CHANGE THIS to your bot's username (e.g., "my_cool_bot")
    BOT_USERNAME = "Oceaan_Luxe_Bot"
    
    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    item_id = f"gold_bar_{amount}"

    # Fetch room users
    room_data = await handler.bot.highrise.get_room_users()
    room_users = room_data.content

    # Logic for /tip all
    if target_input == "all":
        # 1. Map user-provided amount to official Highrise internal item IDs
        # If your bot is failing, it's likely because "gold_bar_1" isn't the correct internal string.
        # This mapping ensures accuracy.
        item_map = {
            "1": "gold_bar_1",
            "5": "gold_bar_5",
            "10": "gold_bar_10",
            "50": "gold_bar_50",
            "100": "gold_bar_100",
            "500": "gold_bar_500",
            "1000": "gold_bar_1k",
            "5000": "gold_bar_5k",
            "10000": "gold_bar_10k"
        }
        
        real_item_id = item_map.get(amount)
        if not real_item_id:
            await handler.bot.highrise.chat("❌ Invalid amount. Use 1, 5, 10, 50, 100, 500, 1000, 5000, 10000.")
            return

        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for user_obj, _ in room_users:
            if user_obj.username.lower() == user.username.lower() or user_obj.username.lower() == BOT_USERNAME.lower():
                continue
                
            try:
                # Use the mapped ID instead of the f-string
                await handler.bot.highrise.tip_user(user_obj.id, real_item_id)
                count += 1
                await asyncio.sleep(1.2) 
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # Logic for /tip @username
    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        
        if not target:
            await handler.bot.highrise.chat("❌ User not found.")
            return
            
        if target.username.lower() == BOT_USERNAME.lower():
            await handler.bot.highrise.chat("❌ I cannot tip myself.")
            return

        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:50]}")
