from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [@username/all] [amount]")
        return

    target = parts[1].lower()
    amount_str = parts[2]
    
    # Item ID Map
    tip_map = {"1": "gold_bar_1", "5": "gold_bar_5", "10": "gold_bar_10", "50": "gold_bar_50"}
    item_id = tip_map.get(amount_str, "gold_bar_1")

    # LOGIC: TIP ALL
    if target == "all":
        room_users = await handler.bot.highrise.get_room_users()
        count = 0
        for u, pos in room_users.content:
            if u.id != user.id: # Don't tip the sender
                try:
                    await handler.bot.highrise.tip_user(u.id, item_id)
                    count += 1
                except Exception: continue
        await handler.bot.highrise.chat(f"💰 Tipped {count} people {amount_str} gold each!")

    # LOGIC: TIP INDIVIDUAL
    else:
        target_name = target.lstrip("@").lower()
        room_users = await handler.bot.highrise.get_room_users()
        target_id = None
        for u, pos in room_users.content:
            if u.username.lower() == target_name:
                target_id = u.id
                break
        
        if target_id:
            try:
                await handler.bot.highrise.tip_user(target_id, item_id)
                await handler.bot.highrise.chat(f"✅ Tipped @{target_name} {amount_str} gold!")
            except Exception as e:
                await handler.bot.highrise.chat(f"❌ Failed: {e}")
        else:
            await handler.bot.highrise.chat("❌ User not found.")
