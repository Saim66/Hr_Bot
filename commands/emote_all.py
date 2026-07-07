import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_all_emote(handler, emote_id):
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # This will print the EXACT reason to your Railway Logs
                    logger.error(f"DEBUG: Failed to send {emote_id} to {user.username}. Error: {e}")
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Handle Stop Commands
    if len(parts) == 1 and (parts[0].lower() in ["/stop", "0"]):
        if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 Stopped.")
        return

    # 2. Handle Start Command
    if len(parts) < 2:
        return
    
    # This logic forces the emote- prefix. 
    # If you type 'dance', it becomes 'emote-dance'
    raw_name = parts[1].lower()
    emote_id = f"emote-{raw_name}" if not raw_name.startswith("emote-") else raw_name
    
    # Start the loop
    if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
        handler.all_loop_task.cancel()
    
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {emote_id}")
