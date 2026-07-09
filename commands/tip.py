import asyncio

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower()
    
    # Helper to validate and send a single tip
    async def send_tip(target_id, amount):
        item_id = f"gold_bar_{amount}"
        try:
            # Highrise API call
            await handler.bot.highrise.tip_user(target_id, item_id)
            return True
        except Exception as e:
            print(f"DEBUG: Tip failed for {target_id}: {e}")
            return False

    # Logic for /tipall [amount]
    if cmd == "/tipall":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /tipall [amount]")
            return
        
        amount = parts[1].lower().replace("gold", "")
        room_users = await handler.bot.highrise.get_room_users()
        
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        # Iterate over the room_users content
        for entry in room_users.content:
            target_user = entry[0] 
            
            # Skip the sender to prevent self-tipping errors
            if target_user.id != user.id:
                # Add a mandatory delay for multiple transactions
                await asyncio.sleep(0.8) 
                success = await send_tip(target_user.id, amount)
                if success:
                    count += 1
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount = parts[2].lower().replace("gold", "")
        
        room_users = await handler.bot.highrise.get_room_users()
        # Find the target
        target_entry = next((entry for entry in room_users.content if entry[0].username.lower() == target_name), None)
        
        if target_entry:
            target_id = target_entry[0].id
            success = await send_tip(target_id, amount)
            if success:
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount} gold!")
            else:
                await handler.bot.highrise.chat(f"❌ Failed to tip @{target_name}. Check bot logs.")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
