import asyncio

async def execute(handler, user, message):
    # Split the message to get the command and the amount
    args = message.split()
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tipall [amount]")
        return

    # Extract the amount (e.g., '1')
    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # Validate Item ID
    valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100", 
                 "gold_bar_500", "gold_bar_1000", "gold_bar_5000", "gold_bar_10000"]
    
    if item_id not in valid_ids:
        await handler.bot.highrise.chat("❌ Invalid amount. Supported: 1, 5, 10, 50, 100, 500, 1000, 5000, 10000.")
        return

    # Fetch room users
    room_users = (await handler.bot.highrise.get_room_users()).content
    
    # Filter: Exclude the user who sent the command
    targets = [u for u, pos in room_users if u.id != user.id]
    
    await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} people {amount} gold...")
    
    count = 0
    for target_user in targets:
        try:
            # Send the tip
            await handler.bot.highrise.tip_user(target_user.id, item_id)
            count += 1
            # Delay is crucial to prevent API rate-limiting
            await asyncio.sleep(1.2) 
        except Exception as e:
            print(f"Failed to tip {target_user.username}: {e}")
            continue
            
    await handler.bot.highrise.chat(f"✅ Finished! Successfully sent {amount} gold to {count} people.")
