import asyncio

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower()
    
    # Logic for /tipall [amount]
    if cmd == "/tipall":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /tipall [amount]")
            return
        
        amount = parts[1].lower().replace("gold", "")
        item_id = f"gold_bar_{amount}"
        
        room_users = await handler.bot.highrise.get_room_users()
        count = 0
        await handler.bot.highrise.chat(f"⏳ Attempting to tip everyone {amount} gold...")
        
        for entry in room_users.content:
            target_user = entry[0] 
            
            if target_user.id != user.id:
                try:
                    # Highrise returns a response object; we must ensure it's valid
                    resp = await handler.bot.highrise.tip_user(target_user.id, item_id)
                    await asyncio.sleep(0.8) # Increased delay for reliability
                    count += 1
                except Exception as e:
                    # Log the specific error if the tip fails
                    print(f"Tip failed for {target_user.username}: {e}")
                    continue
        await handler.bot.highrise.chat(f"✅ Finished! Successfully triggered tips for {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount = parts[2].lower().replace("gold", "")
        item_id = f"gold_bar_{amount}"
        
        room_users = await handler.bot.highrise.get_room_users()
        target_id = None
        for entry in room_users.content:
            u = entry[0]
            if u.username.lower() == target_name:
                target_id = u.id
                break
        
        if target_id:
            try:
                await handler.bot.highrise.tip_user(target_id, item_id)
                await handler.bot.highrise.chat(f"✅ Tip request sent to @{target_name}!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Tip failed: Check bot gold balance.")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
