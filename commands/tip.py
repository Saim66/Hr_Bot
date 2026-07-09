import asyncio
from highrise.models import CurrencyItem

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /tip [all/@username] [amount]")
        return

    BOT_USERNAME = "Oceaan_Luxe_Bot"
    target_input = parts[1].replace("@", "").lower()
    amount = parts[2]
    
    # Use the official currency ID format
    item_id = f"gold_bar_{amount}"

    room_data = await handler.bot.highrise.get_room_users()
    room_users = room_data.content

    if target_input == "all":
        await handler.bot.highrise.chat(f"⏳ Tipping everyone {amount} gold...")
        count = 0
        
        for user_obj, _ in room_users:
            if user_obj.username.lower() == user.username.lower() or user_obj.username.lower() == BOT_USERNAME.lower():
                continue
            
            try:
                # DEBUG: Log the attempt in terminal
                print(f"DEBUG: Attempting to tip {user_obj.username} ID:{user_obj.id}")
                
                # EXECUTION: Try both string and object formats
                await handler.bot.highrise.tip_user(user_obj.id, item_id)
                
                count += 1
                await asyncio.sleep(1.5) # Increased delay for stability
            except Exception as e:
                print(f"CRITICAL ERROR Tipping {user_obj.username}: {e}")
        
        await handler.bot.highrise.chat(f"✅ Finished! Successfully tipped {count} people.")

    else:
        target = next((u for u, _ in room_users if u.username.lower() == target_input), None)
        if not target:
            await handler.bot.highrise.chat("❌ User not found.")
            return
            
        try:
            await handler.bot.highrise.tip_user(target.id, item_id)
            await handler.bot.highrise.chat(f"✨ Tipped @{target.username}!")
        except Exception as e:
            await handler.bot.highrise.chat(f"❌ Failed: {str(e)}")
