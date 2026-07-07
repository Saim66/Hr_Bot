import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_all_emote(handler, emote_id):
    try:
        while True:
            # Fetch users in the room
            room_users = await handler.bot.highrise.get_room_users()
            
            for user, position in room_users.content:
                try:
                    # Attempt to send the emote
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # Logs any failures (Forbidden, etc.)
                    logger.error(f"Failed to emote {user.username}: {e}")
            
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. STOP COMMAND
    if parts[0].lower() in ["/stop", "0"] or (len(parts) > 1 and parts[1].lower() in ["/stop", "0"]):
        if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 Emote loop stopped.")
        return

    # 2. START COMMAND
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [name] (e.g., /all dance, /all rest)")
        return
    
    # This takes whatever you type and adds 'emote-' to the front automatically
    raw_name = parts[1].lower()
    emote_id = f"emote-{raw_name}" if not raw_name.startswith("emote-") else raw_name
    
    # Cancel previous loop
    if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
        handler.all_loop_task.cancel()
    
    # Start new loop
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {raw_name}")
