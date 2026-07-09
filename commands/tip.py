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
    
    # 2. Automatically find the bot's own ID from the room session
    # The SDK usually makes the bot's ID available via 'handler.bot.bot_id' 
    # if using the standard highrise-bot-sdk.
    my_bot_id = getattr(handler.bot, 'bot_id', None)

    # 3. Filter targets: Exclude the sender and the bot itself
    targets = [u for u, pos in room_users if u.id != user.id and u.id != my_bot_id]
    
    if not targets:
        await handler.bot.highrise.chat("⚠️ No other users found to tip.")
        return

    await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} people {amount} gold...")
    
    count = 0
    for target_user in targets:
        try:
            await handler.bot.highrise.tip_user(target_user.id, item_id)
            count += 1
            # Delay is mandatory to prevent rate-limiting by Highrise servers
            await asyncio.sleep(1.2) 
        except Exception as e:
            print(f"DEBUG: Failed to tip {target_user.username}: {e}")
            continue
            
    await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")
