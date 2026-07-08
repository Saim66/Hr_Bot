import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [@username/all] [amount]")
        return

    target = parts[1].lower()
    amount_str = parts[2]
    
    # Map amount to valid Highrise Gold Item IDs
    tip_map = {"1": "gold_bar_1", "5": "gold_bar_5", "10": "gold_bar_10", "50": "gold_bar_50"}
    item_id = tip_map.get(amount_str, "gold_bar_1")

    # LOGIC: TIP ALL
    if target == "all":
        room_users = await handler.bot.highrise.get_room_users()
        count = 0
        await handler.bot.highrise.chat(f"⏳ Attempting to tip everyone...")
        
        for u, pos in room_users.content:
            if u.id != user.id:
                try:
                    # Delay added to prevent API rate-limiting issues
                    await handler.bot.highrise.tip_user(u.id, item_id)
                    await asyncio.sleep(0.5) 
                    count += 1
                except Exception as e:
                    print(f"Skipped {u.username}: {e}")
                    continue
        
        await handler.bot.highrise.chat(f"✅ Finished! Tipped {count} people.")

    # LOGIC: TIP INDIVIDUAL
    else:
        target_name = target.lstrip("@").lower()
        room_users = await handler.bot.highrise.get_room_users()
        target_id = next((u.id for u in room_users.content if u.username.lower() == target_name), None)
        
        if target_id:
            try:
                await handler.bot.highrise.tip_user(target_id, item_id)
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name}!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed to tip: {str(e)[:30]}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
