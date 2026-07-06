import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = parts[1]
    emote_id = EMOTE_DICT.get(emote_name)
    if not emote_id:
        await handler.bot.highrise.chat("Emote not found.")
        return

    # Cancel existing if already running
    await handler.stop_all_emotes("all_command")

    async def emote_loop():
        try:
            while True:
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    await handler.bot.highrise.send_emote(emote_id, room_user.id)
                await asyncio.sleep(6) # Loop every 6 seconds
        except asyncio.CancelledError:
            pass

    # Start the task and store it
    handler.tasks["all_command"] = asyncio.create_task(emote_loop())
    await handler.bot.highrise.chat(f"Started looping {emote_name} for everyone!")