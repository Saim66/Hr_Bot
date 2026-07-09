import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    
    # Basic validation to ensure the amount is a number
    if not amount.isdigit():
        await handler.bot.highrise.chat("❌ Amount must be a valid number.")
        return
        
    item_id = f"gold_bar_{amount}"
    bot_id = getattr(handler.bot, 'bot_id', None)

    # Logic for /tip all
    if target_input == "all":
        # Force a fresh fetch of the room users
        await asyncio.sleep(1) 
        room_data = await handler.bot.highrise.get_room_users()
        room_users = room_data.content
        
        print(f"DEBUG: Found {len(room_users)} total users in room.")
        
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for user_obj, _ in room_users:
            # UPDATED: Only skip the bot. This allows you (the sender) to be tipped.
            if user_obj.id == bot_id:
                continue
            
            try:
                print(f"DEBUG: Attempting to tip {user_obj.username}")
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                # Necessary delay to prevent API rate-limit bans
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")
        
    else:
        # Individual tip logic
        room_data = await handler.bot.highrise.get_room_users()
        room_users = room_data.content
        
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        if target:
            if target.id == bot_id:
                await handler.bot.highrise.chat("❌ I cannot tip myself.")
            else:
                await handler.bot.highrise.tip_user(target.id, item_id)
                await handler.bot.highrise.chat(f"✨ Tipped @{target.username}!")
        else:
            await handler.bot.highrise.chat(f"❌ User @{target_input} not found.")
