import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts:
        return
    trigger = parts[0]

    # --- 1. STOP COMMAND (Kills all active loops) ---
    if trigger in ["stop", "0", "/stop"]:
        if user.username.lower() in handler.active_tasks or handler.all_loop_task:
            await stop_all_for_user(handler, user)
            await handler.bot.highrise.chat("⏹️ All emote loops stopped.")
        else:
            await handler.bot.highrise.chat("⚠️ No active loops to stop.")
        return

    # --- 2. DUAL/TARGETED LOOP (e.g., "dance @user") ---
    if trigger in EMOTE_DICT:
        actual_emote = EMOTE_DICT[trigger]
        target_name = parts[1].replace("@", "").lower() if len(parts) > 1 else user.username.lower()
        
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        
        if target:
            await stop_all_for_user(handler, user) # Clear existing
            
            async def dual_loop(u_id, t_id):
                try:
                    while True:
                        if handler.bot.highrise.ws.closed: break
                        await handler.bot.highrise.send_emote(actual_emote, u_id)
                        await handler.bot.highrise.send_emote(actual_emote, t_id)
                        await asyncio.sleep(6)
                except asyncio.CancelledError:
                    pass

            handler.active_tasks[user.username.lower()] = {
                "task": asyncio.create_task(dual_loop(user.id, target.id)),
                "ids": [user.id, target.id]
            }
            await handler.bot.highrise.chat(f"✨ Looping {trigger} for you and @{target.username}!")
            return

    # --- 3. ALL LOOP (e.g., "/all dance") ---
    if trigger == "/all" and len(parts) > 1:
        emote_name = parts[1].lower()
        emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
        
        if emote_id:
            await stop_all_for_user(handler, user)
            
            async def all_loop():
                try:
                    while True:
                        if handler.bot.highrise.ws.closed: break
                        users = (await handler.bot.highrise.get_room_users()).content
                        for u, _ in users:
                            await handler.bot.highrise.send_emote(emote_id, u.id)
                        await asyncio.sleep(6)
                except asyncio.CancelledError:
                    pass
            
            handler.all_loop_task = asyncio.create_task(all_loop())
            await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

async def stop_all_for_user(handler, user):
    name = user.username.lower()
    # Kill Private Loop
    if name in handler.active_tasks:
        data = handler.active_tasks[name]
        data["task"].cancel()
        for uid in data["ids"]:
            # Ensure 'idle-dance-casual' is in your EMOTE_DICT
            idle = EMOTE_DICT.get("idle-dance-casual")
            if idle: await handler.bot.highrise.send_emote(idle, uid)
        del handler.active_tasks[name]
    
    # Kill Global /all Loop
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        handler.all_loop_task = None
