import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts: return
    
    # 1. PERSONAL STOP (Stops ONLY this user's loops)
    if parts[0] in ["stop", "0"]:
        await stop_user_loops(handler, user)
        return

    # 3. TARGETED/INDIVIDUAL LOOP
    if parts[0] in EMOTE_DICT:
        await start_dual_loop(handler, user, parts)

async def start_dual_loop(handler, user, parts):
    actual_emote = EMOTE_DICT[parts[0]]
    target_name = parts[1].replace("@", "").lower() if len(parts) > 1 else user.username.lower()
    
    room_users = (await handler.bot.highrise.get_room_users()).content
    target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
    
    if target:
        # Clear existing loops for this user before starting new one
        await stop_user_loops(handler, user)
        
        async def dual_loop(u_id, t_id):
            try:
                while True:
                    await handler.bot.highrise.send_emote(actual_emote, u_id)
                    await handler.bot.highrise.send_emote(actual_emote, t_id)
                    await asyncio.sleep(6)
            except asyncio.CancelledError: pass

        handler.active_tasks[user.username.lower()] = {
            "task": asyncio.create_task(dual_loop(user.id, target.id)),
            "type": "dual",
            "ids": [user.id, target.id]
        }
        await handler.bot.highrise.chat(f"✨ Looping {parts[0]} for you and @{target.username}!")

async def start_all_loop(handler, user, emote_name):
    emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
    if emote_id:
        # Clear user's previous loops before starting global
        await stop_user_loops(handler, user)
        
        async def all_loop():
            try:
                while True:
                    users = (await handler.bot.highrise.get_room_users()).content
                    for u, _ in users:
                        await handler.bot.highrise.send_emote(emote_id, u.id)
                    await asyncio.sleep(6)
            except asyncio.CancelledError: pass
        
        handler.active_tasks[user.username.lower()] = {
            "task": asyncio.create_task(all_loop()),
            "type": "all",
            "ids": [] # Global doesn't need specific IDs to reset
        }
        await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

async def stop_user_loops(handler, user):
    """Instant stop for the specific user who triggered it."""
    name = user.username.lower()
    if name in handler.active_tasks:
        data = handler.active_tasks[name]
        
        # 1. Cancel the specific task
        data["task"].cancel()
        
        # 2. Reset avatars if it was a dual-loop
        if data["type"] == "dual":
            idle = EMOTE_DICT.get("idle-dance-casual") or "idle"
            for uid in data["ids"]:
                await handler.bot.highrise.send_emote(idle, uid)
        
        del handler.active_tasks[name]
        await handler.bot.highrise.chat(f"⏹️ Stopped your emote loops.")
