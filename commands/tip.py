import asyncio

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lower()

    # Get the latest list of users in the room
    room_users_response = await handler.bot.highrise.get_room_users()
    room_users = room_users_response.content

    # Logic for /tipall [amount]
    if cmd == "/tipall":
        if len(parts) < 2:
            await handler.bot.highrise.chat("Usage: /tipall [amount]")
            return
        
        amount = parts[1].lower().replace("gold", "")
        # Standard Highrise Gold Bar IDs are 'gold_bar_1', 'gold_bar_5', etc.
        item_id = f"gold_bar_{amount}"
        
        targets = [entry[0] for entry in room_users if entry[0].id != user.id]
        
        await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} people {amount} gold...")
        
        count = 0
        for target_user in targets:
            try:
                # Execution
                await handler.bot.highrise.tip_user(target_user.id, item_id)
                count += 1
                print(f"DEBUG: Successfully sent {item_id} to {target_user.username}")
                await asyncio.sleep(1.5) # Mandatory delay
            except Exception as e:
                print(f"DEBUG: Failed to tip {target_user.username}: {e}")
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
        
        target_user = next((entry[0] for entry in room_users if entry[0].username.lower() == target_name), None)
        
        if target_user:
            try:
                await handler.bot.highrise.tip_user(target_user.id, item_id)
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount} gold!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:30]}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
