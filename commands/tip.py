import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Basic validation
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    
    # Map input amounts to official Highrise IDs
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
        await handler.bot.highrise.chat("❌ Invalid amount. Available: 1, 5, 10, 50, 100, 500, 5000, 10000")
        return

    # 2. Get room state
    room_data = await handler.bot.highrise.get_room_users()
    room_users = room_data.content
    bot_id = handler.bot.client.user_id 

    # 3. Logic for /tip all
    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone in the room {amount} gold...")
        count = 0
        
        for user_obj, _ in room_users:
            # Skip the sender and the bot itself using ID
            if user_obj.id == user.id or user_obj.id == bot_id:
                continue
                
            try:
                print(f"DEBUG: Attempting to tip {user_obj.username} (ID: {user_obj.id})")
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                await asyncio.sleep(1.5) # Mandatory stability delay
            except Exception as e:
                print(f"CRITICAL ERROR Tipping {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # 4. Logic for /tip @username
    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        
        if not target:
            await handler.bot.highrise.chat("❌ User not found.")
            return
            
        if target.id == bot_id:
            await handler.bot.highrise.chat("❌ I cannot tip myself.")
            return

        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:50]}")
