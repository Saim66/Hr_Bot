import asyncio
import logging
from emotes import EMOTE_DICT


logger = logging.getLogger(__name__)

# List of common emotes to help handle names without 'emote-' prefix
# If your emote is missing here, the bot will still try the exact name you type
async def run_all_emote(handler, emote_id):
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # Logs any errors (like invalid ID or permission issues)
                    logger.error(f"Error emoting {user.username}: {e}")
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. STOP COMMAND LOGIC
    if len(parts) == 1 and (parts[0].lower() in ["/stop", "0"]):
        if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 Emote loop stopped.")
        return

    # 2. START COMMAND LOGIC
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name] or /stop")
        return
    
    raw_emote = parts[1].lower()
    
    # Automatically add 'emote-' prefix if the user forgot it
    emote_id = raw_emote if raw_emote.startswith("emote-") else f"emote-{raw_emote}"
    
    # Stop existing loop
    if hasattr(handler, 'all_loop_task') and handler.all_loop_task:
        handler.all_loop_task.cancel()
    
    # Start new loop
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {emote_id}")
