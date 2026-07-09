import asyncio

async def execute(handler, user, message):
    parts = message.split()
    
    # Validation: Ensure /tip [target] [amount] is provided
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    item_id = f"gold_bar_{amount}"

    # Verify Gold Amount
    valid_amounts = ["1", "5", "10", "50", "100", "500", "5000", "10000"]
    if amount not in valid_amounts:
        await handler.bot.highrise.chat(f"❌ Invalid amount. Use: {', '.join(valid_amounts)}")
        return

    # Fetch room users
    room_data = await handler.bot.highrise.get_room_users()
    room_users = room_data.content

    # LOGIC: /tip all
    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for user_obj, _ in room_users:
            # Skip the sender and the bot itself (using is_bot property)
            if user_obj.id == user.id or user_obj.is_bot:
                continue
                
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                count += 1
                await asyncio.sleep(1.2)  # REQUIRED: prevents API spam block
            except Exception as e:
                print(f"Failed to tip {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # LOGIC: /tip @user
    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        
        if not target:
            await handler.bot.highrise.chat("❌ User not found in this room.")
            return
            
        if target.is_bot:
            await handler.bot.highrise.chat("❌ Cannot tip the bot.")
            return

        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:50]}")
