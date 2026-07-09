import asyncio

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower()
    
    # Helper to validate and send tips
    async def send_tip(target_id, target_name, amount):
        item_id = f"gold_bar_{amount}"
        try:
            # Tip the user
            await handler.bot.highrise.tip_user(target_id, item_id)
            return True, None
        except Exception as e:
            return False, str(e)

    # Logic for /tipall [amount]
    if cmd == "/tipall":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /tipall [amount]")
            return
        
        amount = parts[1].lower().replace("gold", "")
        room_users = await handler.bot.highrise.get_room_users()
        
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        count = 0
        for entry in room_users.content:
            target_user = entry[0] 
            
            if target_user.id != user.id:
                success, error = await send_tip(target_user.id, target_user.username, amount)
                if success:
                    count += 1
                    await asyncio.sleep(0.8) # Critical for rate limiting
                else:
                    print(f"Failed to tip {target_user.username}: {error}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount = parts[2].lower().replace("gold", "")
        
        room_users = await handler.bot.highrise.get_room_users()
        target_id = next((entry[0].id for entry in room_users.content if entry[0].username.lower() == target_name), None)
        
        if target_id:
            success, error = await send_tip(target_id, target_name, amount)
            if success:
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount} gold!")
            else:
                await handler.bot.highrise.chat(f"❌ Tip failed: {error}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
