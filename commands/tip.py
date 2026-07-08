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
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        
        # Correctly unpack the tuple (User, Position)
        for entry in room_users.content:
            target_user = entry[0]  # The User object is at index 0
            
            if target_user.id != user.id:
                try:
                    await handler.bot.highrise.tip_user(target_user.id, item_id)
                    await asyncio.sleep(0.6) # Slightly longer delay for stability
                    count += 1
                except Exception as e:
                    print(f"Skipped {target_user.username}: {e}")
                    continue
        await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount = parts[2].lower().replace("gold", "")
        item_id = f"gold_bar_{amount}"
        
        room_users = await handler.bot.highrise.get_room_users()
        
        # Correctly access the user object from the tuple
        target_id = None
        for entry in room_users.content:
            u = entry[0] # User is at index 0
            if u.username.lower() == target_name:
                target_id = u.id
                break
        
        if target_id:
            try:
                await handler.bot.highrise.tip_user(target_id, item_id)
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount} gold!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:30]}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
