import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    
    item_map = {
        "1": "gold_bar_1",
        "5": "gold_bar_5",
        "10": "gold_bar_10",
        "50": "gold_bar_50",
        "100": "gold_bar_100",
        "500": "gold_bar_500",
        "5000": "gold_bar_5k",
        "10000": "gold_bar_10k"
    }
    
    item_id = item_map.get(amount)
    if not item_id:
        await handler.bot.highrise.chat("❌ Invalid amount.")
        return

    room_data = await handler.bot.highrise.get_room_users()
    room_users = room_data.content
    
    # FIXED: Retrieve bot_id directly from the highrise object
    bot_id = handler.bot.highrise.bot_id 

    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        count = 0
        
        for user_obj, _ in room_users:
            if user_obj.id == user.id or user_obj.id == bot_id:
                continue
                
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        if not target:
            await handler.bot.highrise.chat("❌ User not found.")
            return
            
        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed.")
