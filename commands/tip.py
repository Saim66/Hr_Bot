import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Validation
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    
    # Use the official ID for gold
    item_id = f"gold_bar_{amount}"

    # 2. Get live room data
    room_users = (await handler.bot.highrise.get_room_users()).content
    
    # Get the bot's ID from the current session
    bot_id = handler.bot.highrise.bot_id

    # 3. /tip all Logic
    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for user_obj, _ in room_users:
            # Skip the sender and the bot itself using ID
            if user_obj.id == user.id or user_obj.id == bot_id:
                continue
                
            try:
                # Perform the tip
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                
                # CRITICAL: Delay for rate limits
                await asyncio.sleep(1.5) 
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")

    # 4. /tip @username Logic
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
            await handler.bot.highrise.chat(f"✨ Tipped {amount}g to @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:30]}")
