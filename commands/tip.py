import asyncio

async def execute(handler, user, message):
    args = message.split()
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tipall [amount]")
        return

    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # 1. Fetch room users
    room_users_response = await handler.bot.highrise.get_room_users()
    room_users = room_users_response.content
    
    # 2. Safely get the bot's own ID without crashing
    # We look for the bot in the room list to find its ID
    bot_id = None
    for u, pos in room_users:
        # Assuming the bot's username is known or it's the only one with a specific trait
        # If you know your bot's username, replace 'YOUR_BOT_USERNAME'
        if u.username.lower() == "YOUR_BOT_USERNAME": 
            bot_id = u.id
            break
            
    # 3. Filter targets: Exclude sender and the bot itself
    targets = [u for u, pos in room_users if u.id != user.id and u.id != bot_id]
    
    if not targets:
        await handler.bot.highrise.chat("⚠️ No other users found to tip.")
        return

    await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} people {amount} gold...")
    
    count = 0
    for target_user in targets:
        try:
            await handler.bot.highrise.tip_user(target_user.id, item_id)
            count += 1
            await asyncio.sleep(1.2) 
        except Exception as e:
            print(f"DEBUG: Failed to tip {target_user.username}: {e}")
            continue
            
    await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")
