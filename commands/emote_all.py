import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_all_emote(handler, emote_id):
    """Loops the specific emote for all users until cancelled."""
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # Logs if the bot lacks permissions (Forbidden) or ID is invalid (Bad Request)
                    logger.error(f"Failed to emote {user.username}: {e}")
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass

async def execute(handler, user, message):
    parts = message.split()
    
    # Check for Stop command
    if len(parts) >= 1 and parts[0].lower() in ["/stop", "0"]:
        if handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 All emotes stopped.")
        return

    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name] or /stop")
        return
    
    # Process emote name
    raw_name = parts[1].lower()
    emote_id = f"emote-{raw_name}" if not raw_name.startswith("emote-") else raw_name
    
    # Cancel previous emote task if it exists (Ensures new emote overrides old)
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
    
    # Start new background task
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {raw_name}")
