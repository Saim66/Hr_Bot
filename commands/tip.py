import asyncio
from highrise import Position

async def execute(handler, user, message):
    args = message.split()
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tipall [amount]")
        return

    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # Refresh room users
    room_users = (await handler.bot.highrise.get_room_users()).content
    
    # Identify bot safely
    bot_id = next((u.id for u, pos in room_users if u.is_bot), None)
    
    # Get all potential targets (exclude sender and bot)
    targets = [u for u, pos in room_users if u.id != user.id and u.id != bot_id]
    
    if not targets:
        await handler.bot.highrise.chat("⚠️ No one else in the room to tip.")
        return

    await handler.bot.highrise.chat(f"⏳ Tipping {len(targets)} users {amount} gold...")
    
    for target in targets:
        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await asyncio.sleep(1.2) # Mandatory delay
        except Exception as e:
            print(f"DEBUG: Failed to tip {target.username}: {e}")
            continue
            
    await handler.bot.highrise.chat(f"✅ Finished tipping {len(targets)} users!")
