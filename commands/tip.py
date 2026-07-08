import asyncio

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower()
    
    # Logic for /tipall [amount]
    if cmd == "/tipall":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /tipall [amount]")
            return
        
        amount_str = parts[1].lower().replace("gold", "")
        item_id = f"gold_bar_{amount_str}"
        
        room_users = await handler.bot.highrise.get_room_users()
        count = 0
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount_str} gold...")
        
        for u, pos in room_users.content:
            if u.id != user.id:
                try:
                    await handler.bot.highrise.tip_user(u.id, item_id)
                    await asyncio.sleep(0.5)
                    count += 1
                except Exception: continue
        await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount_str = parts[2].lower().replace("gold", "")
        item_id = f"gold_bar_{amount_str}"
        
        room_users = await handler.bot.highrise.get_room_users()
        target_id = next((u.id for u in room_users.content if u.username.lower() == target_name), None)
        
        if target_id:
            try:
                await handler.bot.highrise.tip_user(target_id, item_id)
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount_str} gold!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:30]}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
