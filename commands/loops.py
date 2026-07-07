import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    trigger = parts[0]

    # 1. HANDLE EMOTE LOOP
    if trigger in EMOTE_DICT:
        actual_emote = EMOTE_DICT[trigger]
        target_name = parts[1].replace("@", "").lower() if len(parts) > 1 else user.username.lower()
        
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        
        if target:
            # Stop existing loops for this pair to prevent overlap
            if user.username.lower() in handler.active_tasks:
                handler.looping_users[user.username.lower()] = False
                handler.active_tasks[user.username.lower()].cancel()
            
            # Start loop for both
            handler.looping_users[user.username.lower()] = True
            
            # Create a combined task that loops both users
            async def dual_loop():
                try:
                    while handler.looping_users.get(user.username.lower(), False):
                        # Send for both
                        await handler.bot.highrise.send_emote(actual_emote, user.id)
                        await handler.bot.highrise.send_emote(actual_emote, target.id)
                        await asyncio.sleep(6)
                except asyncio.CancelledError:
                    pass

            handler.active_tasks[user.username.lower()] = asyncio.create_task(dual_loop())
            await handler.bot.highrise.chat(f"✨ Looping {trigger} for you and @{target.username}!")
            
        # ... (rest of your code)
    elif trigger in ["stop", "0"]:
        name = user.username.lower()
        if name in handler.active_tasks:
            # 1. Stop the loop task
            handler.looping_users[name] = False
            handler.active_tasks[name].cancel()
            del handler.active_tasks[name]
            
            # 2. INSTANT RESET: Send the 'idle' emote to both users
            # This forces the avatars to stop the previous animation
            await handler.bot.highrise.send_emote("idle-dance-casual", user.id)
            
            # If there was a target in the loop, find them and reset them too
            # (Note: This assumes you stored the target in the loop logic)
            # You may want to track the current target ID in the handler
            
            await handler.bot.highrise.chat(f"⏹️ Stopped your emote loops.")
