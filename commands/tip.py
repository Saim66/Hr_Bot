import asyncio

async def execute(handler, user, message):
    args = message.split()
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tipall [amount]")
        return

    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # 1. Fetch room users
    room_users = (await handler.bot.highrise.get_room_users()).content
    
    # 2. Identify the bot's ID automatically (Safe approach)
    my_bot_id = next((u.id for u, pos in room_users if u.is_bot), None)

    # 3. Filter targets: Exclude sender and the bot itself
    targets = [u for u, pos in room_users if u.id != user.id and u.id != my_bot_id]
    
    if not targets:
        await handler.bot.highrise.chat("⚠️ No other users found to tip.")
        return

    await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} people {amount} gold...")
    
    count = 0
    for target_user in targets:
        try:
            # Execute tip
            await handler.bot.highrise.tip_user(target_user.id, item_id)
            count += 1
            await asyncio.sleep(1.2) # Mandatory to prevent rate limits
        except Exception as e:
            print(f"Failed to tip {target_user.username}: {e}")
            continue
            
    await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")
