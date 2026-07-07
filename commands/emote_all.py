import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. STOP COMMAND
    if len(parts) >= 1 and parts[0].lower() in ["/stop", "0"]:
        if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 All emotes stopped.")
        return

    # 2. START COMMAND
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = parts[1].lower()
    emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
    
    if not emote_id:
        await handler.bot.highrise.chat("❌ Emote not found.")
        return

    # PREVENT CONFLICT: Cancel and Wait
    if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
        handler.all_loop_task.cancel()
        try:
            # Wait a brief moment to ensure the old loop actually exits
            await asyncio.wait_for(handler.all_loop_task, timeout=1.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

    async def emote_loop():
        try:
            while True:
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    try:
                        await handler.bot.highrise.send_emote(emote_id, room_user.id)
                    except Exception:
                        continue
                # Reduced sleep to keep the loop tight
                await asyncio.sleep(6)
        except asyncio.CancelledError:
            raise # Important for clean cancellation

    # Start new task
    handler.all_loop_task = asyncio.create_task(emote_loop())
