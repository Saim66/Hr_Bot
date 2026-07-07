import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Handle Stop logic
    if parts[0].lower() in ["/stop", "0"]:
        if handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 All emotes stopped.")
        return

    # 2. Start logic
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = parts[1].lower()
    # Handle both 'emote-name' and 'name'
    emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
    
    if not emote_id:
        await handler.bot.highrise.chat("❌ Emote not found.")
        return

    # CRITICAL: Cancel the existing global task before starting a new one
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        # Optional: give it a tiny moment to clean up
        await asyncio.sleep(0.1)

    await handler.bot.highrise.chat(f"✨ Starting '{emote_name}' loop for everyone!")

    async def emote_loop():
        try:
            while True:
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    try:
                        await handler.bot.highrise.send_emote(emote_id, room_user.id)
                    except Exception:
                        continue
                await asyncio.sleep(6)
        except asyncio.CancelledError:
            pass

    # Store the task in the specific variable we initialized in CommandHandler
    handler.all_loop_task = asyncio.create_task(emote_loop())
