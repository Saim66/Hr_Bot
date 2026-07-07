import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts:
        return
    trigger = parts[0]

    # 1. HANDLE EMOTE LOOP
    if trigger in EMOTE_DICT:
        actual_emote = EMOTE_DICT[trigger]
        target_name = parts[1].replace("@", "").lower() if len(parts) > 1 else user.username.lower()
        
        # Fetch user and target from current room
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        
        if target:
            # Stop any existing loops for this user before starting new one
            if user.username.lower() in handler.active_tasks:
                await stop_loop(handler, user)
            
            handler.looping_users[user.username.lower()] = True
            
            # Create the loop task
            async def dual_loop(u_id, t_id):
                try:
                    while handler.looping_users.get(user.username.lower(), False):
                        # Verify connection before sending
                        if not handler.bot.highrise.ws or handler.bot.highrise.ws.closed:
                            break
                        
                        await handler.bot.highrise.send_emote(actual_emote, u_id)
                        await handler.bot.highrise.send_emote(actual_emote, t_id)
                        await asyncio.sleep(6)
                except asyncio.CancelledError:
                    pass

            task = asyncio.create_task(dual_loop(user.id, target.id))
            
            # Store task AND target_id to allow clean stop
            handler.active_tasks[user.username.lower()] = {
                "task": task,
                "target_id": target.id
            }
            await handler.bot.highrise.chat(f"✨ Looping {trigger} for you and @{target.username}!")
            
    # 2. HANDLE STOP
    elif trigger in ["stop", "0"]:
        if user.username.lower() in handler.active_tasks:
            await stop_loop(handler, user)
            await handler.bot.highrise.chat(f"⏹️ Stopped your emote loops.")
        else:
            await handler.bot.highrise.chat(f"⚠️ No active loop to stop.")

async def stop_loop(handler, user):
    """Stops the loop and resets both users to idle."""
    name = user.username.lower()
    if name in handler.active_tasks:
        data = handler.active_tasks[name]
        
        # Stop the background task
        handler.looping_users[name] = False
        data["task"].cancel()
        
        # Reset to idle to clear the animation state immediately
        # Ensure 'idle-dance-casual' is in your EMOTE_DICT or change to a valid idle key
        idle_key = "idle-dance-casual"
        if idle_key in EMOTE_DICT:
            await handler.bot.highrise.send_emote(EMOTE_DICT[idle_key], user.id)
            await handler.bot.highrise.send_emote(EMOTE_DICT[idle_key], data["target_id"])
        
        del handler.active_tasks[name]
