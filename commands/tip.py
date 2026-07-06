# commands/tip.py
import asyncio

async def execute(handler, user, message):
    args = message.split()[1:]
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tip [@username/all] [1, 5, 10, ...]")
        return

    target_input = args[0].replace("@", "").lower()
    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # Verify the item_id is valid
    valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100",
                 "gold_bar_500", "gold_bar_1k", "gold_bar_5000", "gold_bar_10k"]
    
    if item_id not in valid_ids:
        await handler.bot.highrise.chat("❌ Invalid amount.")
        return

    room_users = (await handler.bot.highrise.get_room_users()).content

    if target_input == "all":
        for user_obj, _ in room_users:
            if user_obj.id == handler.bot.bot_id: continue
            try:
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                await asyncio.sleep(1)
            except Exception as e: print(f"Failed to tip {user_obj.username}: {e}")
    else:
        target = next((r for r, _ in room_users if r.username.lower() == target_input), None)
        if target:
            try:
                await handler.bot.highrise.tip_user(target.id, item_id)
                await handler.bot.highrise.chat(f"✨ Tipped {amount} gold to @{target.username}!")
            except Exception as e: await handler.bot.highrise.chat(f"❌ Failed: {e}")