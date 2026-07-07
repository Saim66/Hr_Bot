import asyncio
import logging
from emotes import EMOTE_DICT

logger = logging.getLogger(__name__)

async def run_all_emote(handler, emote_id):
    """Background task that loops the emote for all users."""
    try:
        while True:
            # Fetch users currently in the room
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # Logs individual failures (e.g., user left or permission denied)
                    logger.debug(f"Could not emote {user.username}: {e}")
            
            # Wait for 6 seconds as per Highrise emote duration
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        # Gracefully stop the loop when task is cancelled
        pass

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. STOP COMMAND LOGIC
    # Handles '/stop', '/all /stop', or '0'
    if parts[0].lower() in ["/stop", "0"] or (len(parts) > 1 and parts[1].lower() in ["/stop", "0"]):
        if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 Emote loop stopped.")
        return

    # 2. START COMMAND LOGIC
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name] (e.g., /all dance)")
        return
    
    raw_emote = parts[1].lower()
    
    # Auto-prefix 'emote-' if missing
    emote_id = raw_emote if raw_emote.startswith("emote-") else f"emote-{raw_emote}"
    
    # Optional Validation: Check if the emote exists in your EMOTE_DICT
    # Comment this block out if you want to allow any string
    if raw_emote not in EMOTE_DICT and emote_id not in EMOTE_DICT:
        await handler.bot.highrise.chat(f"❌ '{raw_emote}' is not a recognized emote.")
        return

    # Cancel any existing loop before starting a new one
    if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
        handler.all_loop_task.cancel()
    
    # Start the new loop
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {emote_id}")
