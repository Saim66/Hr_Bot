import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. STOP COMMAND
    if len(parts) >= 1 and parts[0].lower() in ["/stop", "0"]:
        # Use the handler method to cancel everything
        await handler.stop_all_emotes("all_command")
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

    # FORCE STOP PREVIOUS TASK IMMEDIATELY
    # Calling this first ensures the old loop dies before we start the new one
    await handler.stop_all_emotes("all_command")

    await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

    async def emote_loop():
        try:
            while True:
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    try:
                        # We send the emote, but if this task is cancelled, 
                        # the loop breaks instantly.
                        await handler.bot.highrise.send_emote(emote_id, room_user.id)
                    except Exception:
                        continue
                
                # IMPORTANT: Using wait_for allows the loop to break 
                # immediately when cancelled, rather than waiting 6 seconds.
                await asyncio.wait_for(asyncio.sleep(6), timeout=6.0)
        except asyncio.CancelledError:
            pass # Task was cancelled, exit cleanly

    # Start the task
    handler.all_loop_task = asyncio.create_task(emote_loop())
