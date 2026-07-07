import asyncio
from emotes import EMOTE_DICT

async def run_all_emote(handler, emote_id):
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_id, user.id)
                except Exception as e:
                    # ADD THIS LINE TO SEE THE ERROR IN YOUR LOGS
                    logger.error(f"Failed to send emote {emote_id} to {user.username}: {e}")
            await asyncio.sleep(6)
    except asyncio.CancelledError:
        pass


async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        return
    
    emote_id = parts[1]
    
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        handler.all_loop_task = None
    
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_id))
    await handler.bot.highrise.chat(f"📢 Emote {emote_id} started for everyone!")
