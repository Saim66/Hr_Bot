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

    # 2. TARGETED/INDIVIDUAL LOOP
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
            except asyncio.CancelledError: 
                pass

        handler.active_tasks[user.username.lower()] = {
            "task": asyncio.create_task(dual_loop(user.id, target.id)),
            "type": "dual",
            "ids": [user.id, target.id]
        }
        await handler.bot.highrise.chat(f"✨ Looping {parts[0]} for you and @{target.username}!")
    else:
        await handler.bot.highrise.chat(f"❌ User @{target_name} not found in this room.")

async def stop_user_loops(handler, user):
    """Instant stop for the specific user who triggered it."""
    name = user.username.lower()
    if name in handler.active_tasks:
        data = handler.active_tasks[name]
        
        # 1. Cancel the specific task
        data["task"].cancel()
        
        # 2. Reset avatars
        idle = EMOTE_DICT.get("idle-dance-casual") or "idle"
        for uid in data.get("ids", []):
            try:
                await handler.bot.highrise.send_emote(idle, uid)
            except Exception:
                continue
        
        del handler.active_tasks[name]
        await handler.bot.highrise.chat(f"⏹️ Stopped your emote loops.")
