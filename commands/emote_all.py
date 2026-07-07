import asyncio
from emotes import EMOTE_DICT
import asyncio
import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_id]")
        return
    
    emote_id = parts[1]
    
    # 1. Stop any existing global loop
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        handler.all_loop_task = None
    
    # 2. Start the new loop as a background task
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {emote_id}")

async def run_all_emote(handler, emote_id):
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception:
                    continue
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass 
())