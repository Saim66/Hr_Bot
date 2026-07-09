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
        
        await handler.bot.highrise.chat(f"⏳ Tipping {len(room_users)-1} people {amount} gold...")
        
        count = 0
        for entry in room_users:
            target_user = entry[0] 
            
            # Skip the sender and the bot itself (if bot is in the list)
            if target_user.id != user.id and target_user.id != handler.bot.bot_id:
                try:
                    # Attempt the tip
                    await handler.bot.highrise.tip_user(target_user.id, f"gold_bar_{amount}")
                    count += 1
                    # Small delay to keep the connection healthy
                    await asyncio.sleep(1.2) 
                except Exception as e:
                    print(f"DEBUG: Could not tip {target_user.username}: {e}")
                    continue
        
        await handler.bot.highrise.chat(f"✅ Done! Successfully sent tips to {count} people.")

    # Logic for /tip @user [amount]
    elif cmd == "/tip":
        if len(parts) < 3:
            await handler.bot.highrise.chat("Usage: /tip @username [amount]")
            return
        
        target_name = parts[1].lstrip("@").lower()
        amount = parts[2].lower().replace("gold", "")
        
        target_user = next((entry[0] for entry in room_users if entry[0].username.lower() == target_name), None)
        
        if target_user:
            try:
                await handler.bot.highrise.tip_user(target_user.id, f"gold_bar_{amount}")
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount} gold!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed: {str(e)[:30]}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
