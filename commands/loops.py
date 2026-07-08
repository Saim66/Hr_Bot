import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts: return
    
    # Check for stop trigger first
    if parts[0] in ["stop", "0", "/stop"]:
        await stop_all_for_user(handler, user)
        await handler.bot.highrise.chat("⏹️ Stopped all loops.")
        return

    # Check if command is /all
    if parts[0] == "/all" and len(parts) > 1:
        await start_all_loop(handler, user, parts[1])
        return

    # Check if command is a direct emote (e.g., "dance @target")
    if parts[0] in EMOTE_DICT:
        await start_dual_loop(handler, user, parts)
        return

async def start_dual_loop(handler, user, parts):
    actual_emote = EMOTE_DICT[parts[0]]
    # Handle target: Default to user if no target provided
    target_name = parts[1].replace("@", "").lower() if len(parts) > 1 else user.username.lower()
    
    room_users = (await handler.bot.highrise.get_room_users()).content
    target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
    
    if target:
        # Kill anything else running before starting
        await stop_all_for_user(handler, user)
        
        async def dual_loop(u_id, t_id):
            try:
                while True:
                    await handler.bot.highrise.send_emote(actual_emote, u_id)
                    await handler.bot.highrise.send_emote(actual_emote, t_id)
                    await asyncio.sleep(6)
            except asyncio.CancelledError: pass

        handler.active_tasks[user.username.lower()] = {
            "task": asyncio.create_task(dual_loop(user.id, target.id)),
            "ids": [user.id, target.id]
        }
        await handler.bot.highrise.chat(f"✨ Looping {parts[0]} for you and @{target.username}!")

async def start_all_loop(handler, user, emote_name):
    emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
    if emote_id:
        # Kill anything else running before starting
        await stop_all_for_user(handler, user)
        
        async def all_loop():
            try:
                while True:
                    users = (await handler.bot.highrise.get_room_users()).content
                    for u, _ in users:
                        await handler.bot.highrise.send_emote(emote_id, u.id)
                    await asyncio.sleep(6)
            except asyncio.CancelledError: pass
        
        handler.all_loop_task = asyncio.create_task(all_loop())
        await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

async def stop_all_for_user(handler, user):
    """The Universal 'Kill Switch'"""
    name = user.username.lower()
    
    # 1. Kill Targeted Loops
    if name in handler.active_tasks:
        data = handler.active_tasks[name]
        data["task"].cancel()
        idle = EMOTE_DICT.get("idle-dance-casual")
        if idle:
            for uid in data["ids"]:
                await handler.bot.highrise.send_emote(idle, uid)
        del handler.active_tasks[name]
    
    # 2. Kill /all Loop
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        handler.all_loop_task = None
