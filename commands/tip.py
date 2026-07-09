import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Validation
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    item_id = f"gold_bar_{amount}"

    # 2. Fetch room users
    room_users = (await handler.bot.highrise.get_room_users()).content

    # 3. /tip all Logic
    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for user_obj, _ in room_users:
            # Skip the sender and the bot itself
            if user_obj.id == user.id or user_obj.is_bot:
                continue
                
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                await asyncio.sleep(1.2) # Mandatory delay
            except Exception as e:
                # Log failures to the terminal for debugging
                print(f"Failed to tip {user_obj.username}: {e}")
                continue
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # 4. /tip @username Logic
    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        
        if not target:
            await handler.bot.highrise.chat("❌ User not found.")
            return
            
        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:50]}")
